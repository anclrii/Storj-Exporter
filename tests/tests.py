from storj_exporter import StorjCollector, MetricsHandler
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily, REGISTRY
import json

class StorjCollectorMock(StorjCollector):
  # def __init__(self):
    # self.node_data = None
    # self.storj_host_address = os.environ.get('STORJ_HOST_ADDRESS', '127.0.0.1')
    # self.storj_api_port = os.environ.get('STORJ_API_PORT', '14002')
    # self.storj_collectors = os.environ.get('STORJ_COLLECTORS', 'payout sat').split()
    # self.baseurl = 'http://' + self.storj_host_address + ':' + self.storj_api_port + '/api/'
    
  def call_api(self, path):
    response = None
    try:
      response=requests.get(url = self.baseurl + path).json()
    except:
      pass
    return response
   
  def get_node_data(self):
    with open('test_data/node_data.json') as json_file:
      self.node_data = json.load(json_file)

  def get_node_payout_data(self):
    with open('test_data/node_payout_data.json') as json_file:
      self.node_data['payout'] = None # json.load(json_file)

  def get_sat_data(self, sat):
    with open('test_data/sat_data.json') as json_file:
      sat['sat_data'] = json.load(json_file)
    if isinstance(sat['sat_data'], dict):
      sat['sat_data'].update(self.sum_sat_daily_keys(sat['sat_data'], 'bandwidthDaily', ['repair','audit','usage'], 'egress'))
      sat['sat_data'].update(self.sum_sat_daily_keys(sat['sat_data'], 'bandwidthDaily', ['repair','usage'], 'ingress'))
          
  def collect(self):
    yield from self.add_node_metrics()
    if self.node_data:
      yield from self.add_payout_metrics()
      yield from self.add_sat_metrics()

if __name__ == '__main__':
  REGISTRY.register(StorjCollectorMock())