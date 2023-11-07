#!/usr/bin/env python

import os
import signal
import threading
import time
import json
import logging
from wsgiref.simple_server import make_server
from prometheus_client import MetricsHandler, make_wsgi_app
from prometheus_client.core import REGISTRY
from prometheus_client.exposition import ThreadingWSGIServer
from api_wrapper import ApiClient
from collectors import NodeCollector, SatCollector, PayoutCollector

logger = logging.getLogger(__name__)


class GracefulKiller:
    kill_now = False
    signals = {
        signal.SIGINT: 'SIGINT',
        signal.SIGTERM: 'SIGTERM'
    }

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print("\nReceived {} signal, exiting ...".format(self.signals[signum]))
        self.kill_now = True


class HTTPRequestHandler(MetricsHandler):
    def do_GET(self):
        if self.path == "/status":
            message = dict(status="alive")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(message), "utf-8"))
        else:
            return MetricsHandler.do_GET(self)

    def log_message(self, format, *args):
        logger.debug("Client request: %s %s" % (self.address_string(), format % args))


def start_wsgi_server(port, addr='', registry=REGISTRY):
    """Starts a WSGI server for prometheus metrics as a daemon thread."""
    logger.info(f'Starting WSGI server on port {port}')
    app = make_wsgi_app(registry)
    httpd = make_server(addr, port, app, ThreadingWSGIServer,
                        handler_class=HTTPRequestHandler)
    t = threading.Thread(target=httpd.serve_forever)
    t.daemon = True
    t.start()
    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(1)
    logger.info("Shutting down WSGI server")


def main():
    """Read in environment variables"""
    storj_host_address = os.environ.get('STORJ_HOST_ADDRESS', '127.0.0.1')
    storj_api_port = os.environ.get('STORJ_API_PORT', '14002')
    storj_api_timeout = int(os.environ.get('STORJ_API_TIMEOUT', '90'))
    storj_exporter_port = int(os.environ.get('STORJ_EXPORTER_PORT', '9651'))
    storj_collectors = os.environ.get('STORJ_COLLECTORS', 'payout sat').split()
    log_level = os.environ.get('STORJ_EXPORTER_LOG_LEVEL', 'INFO').upper()

    """Setup logging."""
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    """Instantiate api client and node collector"""
    baseurl = 'http://' + storj_host_address + ':' + storj_api_port
    logger.info(f'Starting storj exporter on port {storj_exporter_port}, '
                f'connecting to {baseurl} with collectors {storj_collectors} enabled')
    client = ApiClient(baseurl, timeout=storj_api_timeout)
    node_collector = NodeCollector(client)
    logger.info('Registering node collector')
    REGISTRY.register(node_collector)

    """Instantiate and register optional collectors"""
    if 'payout' in storj_collectors:
        payout_collector = PayoutCollector(client)
        logger.info('Registering payout collector')
        REGISTRY.register(payout_collector)
    if 'sat' in storj_collectors:
        sat_collector = SatCollector(client)
        logger.info('Registering sat collector')
        REGISTRY.register(sat_collector)

    start_wsgi_server(storj_exporter_port, '')


if __name__ == '__main__':
    main()
