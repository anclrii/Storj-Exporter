#!/usr/bin/env python

import os
import signal
import threading
import time
from wsgiref.simple_server import make_server
from prometheus_client import MetricsHandler, make_wsgi_app
from prometheus_client.core import REGISTRY
from prometheus_client.exposition import ThreadingWSGIServer
from api_wrapper import ApiClient
from collectors import NodeCollector, SatCollector


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
        """Log nothing."""


def start_wsgi_server(port, addr='', registry=REGISTRY):
    """Starts a WSGI server for prometheus metrics as a daemon thread."""
    app = make_wsgi_app(registry)
    httpd = make_server(addr, port, app, ThreadingWSGIServer,
                        handler_class=HTTPRequestHandler)
    t = threading.Thread(target=httpd.serve_forever)
    t.daemon = True
    t.start()
    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(1)

def print_samples(registry):
    for metric in registry.collect():
        for s in metric.samples:
            print(s)

if __name__ == '__main__':
    """Read environment variables"""
    storj_host_address = os.environ.get('STORJ_HOST_ADDRESS', '127.0.0.1')
    storj_api_port = os.environ.get('STORJ_API_PORT', '14002')
    storj_exporter_port = int(os.environ.get('STORJ_EXPORTER_PORT', '9651'))
    storj_collectors = os.environ.get('STORJ_COLLECTORS', 'payout sat').split()

    """Instantiate api client and node collector"""
    baseurl = 'http://' + storj_host_address + ':' + storj_api_port
    client = ApiClient(baseurl)
    node_collector = NodeCollector(client)
    REGISTRY.register(node_collector)

    """Instantiate and register optional collectors"""
    # if 'payout' in storj_collectors:
    #     payout_collector = PayoutCollector(client)
    #     REGISTRY.register(payout_collector)
    if 'sat' in storj_collectors:
        sat_collector = SatCollector(client)
        REGISTRY.register(sat_collector)

    start_wsgi_server(storj_exporter_port, '')

