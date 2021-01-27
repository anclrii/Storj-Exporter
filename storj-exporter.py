import os
import signal
import time
import requests
import json
import threading
from wsgiref.simple_server import make_server
from prometheus_client import MetricsHandler, make_wsgi_app
from prometheus_client.exposition import ThreadingWSGIServer
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily, REGISTRY

class StorjCollector(object):
  def __init__(self):
    self.node_data = None
    self.storj_host_address = os.environ.get('STORJ_HOST_ADDRESS', '127.0.0.1')
    self.storj_api_port = os.environ.get('STORJ_API_PORT', '14002')
    self.storj_collectors = os.environ.get('STORJ_COLLECTORS', 'payout sat').split()
    self.baseurl = 'http://' + self.storj_host_address + ':' + self.storj_api_port + '/api/'
    
  def call_api(self, path):
    response = None
    try:
      response=requests.get(url = self.baseurl + path).json()
    except:
      pass
    return response
   
  def get_node_data(self):
    self.node_data = self.call_api('sno/')

  def get_node_payout_data(self):
    self.node_data['payout'] = self.call_api('sno/estimated-payout')

  def get_sat_data(self, sat):
    sat['sat_data'] = self.call_api('sno/satellite/' + sat['id'])
    if isinstance(sat['sat_data'], dict):
      sat['sat_data'].update(self.sum_sat_daily_keys(sat['sat_data'], 'bandwidthDaily', ['repair','audit','usage'], 'egress'))
      sat['sat_data'].update(self.sum_sat_daily_keys(sat['sat_data'], 'bandwidthDaily', ['repair','usage'], 'ingress'))
          
  def sum_sat_daily_keys(self, daily_data_dict, daily_data_key, data_types, daily_data_path):
    sum_month_dict = daily_data_dict['sum_' + daily_data_key + '_' + daily_data_path ] = {}
    if daily_data_key in daily_data_dict and isinstance(daily_data_dict[daily_data_key], list):
      for day in daily_data_dict[daily_data_key]:
        for data_type in data_types:
          if data_type not in sum_month_dict:
            sum_month_dict[data_type] = 0.0
          if daily_data_path in day and data_type in day[daily_data_path]: 
            day_value = day[daily_data_path][data_type]
            if day_value:
              sum_month_dict.update({data_type: (sum_month_dict[data_type] + day_value)})
    return daily_data_dict

  def dict_to_metric(self, dict, metric_name, documentation, metric_family, keys, labels,label_values=[] ):
    if dict:
      metric = metric_family(metric_name, documentation, labels=labels)
      for key in keys:
        value = 0.0
        if key in dict:
          key_label_values = [key] + label_values
          if metric_family == InfoMetricFamily:
            value = {key : str(dict[key])}
          elif isinstance(dict[key],(int, float)):
            value = dict[key]
          metric.add_metric(key_label_values, value)      
      yield metric

  def safe_list_get(self, list, idx, default={}):
    try:
      return list[idx]
    except:
      return default

  def add_node_metrics(self):
    self.get_node_data()
    if self.node_data:
      labels          = ['type']
      metric_family   = GaugeMetricFamily

      metric_name     = 'storj_node'
      data            = self.node_data
      documentation   = 'Storj node info'
      keys            = ['nodeID','wallet','lastPinged','upToDate','version','allowedVersion','startedAt']
      yield from self.dict_to_metric(data, metric_name, documentation, InfoMetricFamily, keys, labels) 

      metric_name     = 'storj_total_diskspace'
      data            = self.node_data.get('diskSpace', None)
      documentation   = 'Storj total diskspace metrics'
      keys            = ['used','available','trash']
      yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels)

      data            = self.node_data.get('bandwidth', None)
      metric_name     = 'storj_total_bandwidth'
      documentation   = 'Storj total bandwidth metrics'
      keys            = ['used','available']
      yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels)

      ## to be deprecated
      for key in ['nodeID','wallet','lastPinged','upToDate','version','allowedVersion','startedAt']:
        if key in self.node_data:
          value = str(self.node_data[key])
          metric = InfoMetricFamily('storj_' + key, 'Storj ' + key, value={key : value})
          yield metric
      ##############

  def add_payout_metrics(self):
    if 'payout' in self.storj_collectors:
      self.get_node_payout_data()
      metric_name     = 'storj_payout_currentMonth'
      data            = self.node_data.get('payout', {}).get('currentMonth', None)
      documentation   = 'Storj estimated payouts for current month'
      keys            = ['egressBandwidth', 'egressBandwidthPayout', 'egressRepairAudit', 'egressRepairAuditPayout', 'diskSpace', 'diskSpacePayout', 'heldRate', 'payout', 'held']
      labels          = ['type']
      metric_family   = GaugeMetricFamily
      yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels)

  def add_sat_metrics(self):
    if 'satellites' in self.node_data:
      for sat in self.node_data['satellites']:
        sat.update({'disqualified': 1}) if sat['disqualified'] else sat.update({'disqualified': 0})
        sat.update({'suspended': 1}) if sat['suspended'] else sat.update({'suspended': 0})
        metric_name     = 'storj_sat_summary'
        data            = sat
        documentation   = 'Storj satellite summary metrics'
        keys            = ['disqualified','suspended']
        labels          = ['type', 'satellite', 'url']
        label_values    = [sat['id'], sat['url']]
        metric_family   = GaugeMetricFamily
        yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels, label_values)
        yield from self.add_extended_sat_metrics(sat)    
  
  def add_extended_sat_metrics(self, sat):
    if 'sat' in self.storj_collectors:
      self.get_sat_data(sat)
      labels          = ['type', 'satellite', 'url']
      label_values    = [sat['id'], sat['url']]
      metric_family   = GaugeMetricFamily

      if 'sat_data' in sat:
        metric_name     = 'storj_sat_nodeJoinedAt'
        data            = sat['sat_data']
        documentation   = 'Storj Node joined satellite at'
        keys            = ['nodeJoinedAt']
        yield from self.dict_to_metric(data, metric_name, documentation, InfoMetricFamily, keys, labels, label_values)

        metric_name     = 'storj_sat_summary'
        data            = sat['sat_data']
        documentation   = 'Storj satellite summary metrics'
        keys            = ['storageSummary','bandwidthSummary','egressSummary','ingressSummary','onlineScore']
        yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels, label_values)

        metric_name     = 'storj_sat_audit'
        data            = sat['sat_data'].get('audits', None)
        documentation   = 'Storj satellite audit metrics'
        keys            = ['auditScore','suspensionScore','onlineScore','satelliteName']
        yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels, label_values)

        metric_name     = 'storj_sat_day_egress'
        data            = self.safe_list_get(sat['sat_data'].get('bandwidthDaily', [{}]), -1).get('egress', None)
        documentation   = 'Storj satellite egress since current day start'
        keys            = ['repair','audit','usage']
        yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels, label_values)

        metric_name     = 'storj_sat_day_ingress'
        data            = self.safe_list_get(sat['sat_data'].get('bandwidthDaily', [{}]), -1).get('ingress', None)
        documentation   = 'Storj satellite ingress since current day start'
        keys            = ['repair','usage']
        yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels, label_values)

        metric_name     = 'storj_sat_day_storage'
        data            = self.safe_list_get(sat['sat_data'].get('storageDaily', None),-1)
        documentation   = 'Storj satellite data stored on disk since current day start'
        keys            = ['atRestTotal']
        yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels, label_values)        

        metric_name     = 'storj_sat_month_egress'
        data            = sat['sat_data'].get('sum_bandwidthDaily_egress', None)
        documentation   = 'Storj satellite egress since current month start'
        keys            = ['repair','audit','usage']
        yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels, label_values)

        metric_name     = 'storj_sat_month_ingress'
        data            = sat['sat_data'].get('sum_bandwidthDaily_ingress', None)
        documentation   = 'Storj satellite ingress since current month start'
        keys            = ['repair','usage']
        yield from self.dict_to_metric(data, metric_name, documentation, metric_family, keys, labels, label_values)

  def collect(self):
    yield from self.add_node_metrics()
    if self.node_data:
      yield from self.add_payout_metrics()
      yield from self.add_sat_metrics()


class HTTPRequestHandler(MetricsHandler):
  def do_GET(self):

    if self.path == "/status":
      message = dict(status="alive")
      self.send_response(200)
      self.end_headers()
      self.wfile.write(bytes(json.dumps(message), "utf-8"))

    else:
      return MetricsHandler.do_GET(self)
      #self.send_error(404)

  def log_message(self, format, *args):
    """Log nothing."""

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

def start_wsgi_server(port, addr='', registry=REGISTRY):
  """Starts a WSGI server for prometheus metrics as a daemon thread."""
  app = make_wsgi_app(registry)
  httpd = make_server(addr, port, app, ThreadingWSGIServer, handler_class=HTTPRequestHandler)
  t = threading.Thread(target=httpd.serve_forever)
  t.daemon = True
  t.start()

if __name__ == '__main__':
  killer = GracefulKiller()
  REGISTRY.register(StorjCollector())
  storj_exporter_port = int(os.environ.get('STORJ_EXPORTER_PORT', '9651'))
  start_wsgi_server(storj_exporter_port,'')
  while not killer.kill_now: time.sleep(1)