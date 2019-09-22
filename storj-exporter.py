import time
import requests
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily, REGISTRY

class StorjCollector(object):
  def __init__(self):
    self.data = self.get_data()
    self.satellites = self.get_satellites()
    self.sat_data = self.get_sat_data()

  def call_api(self,path):
    response=requests.get(url = "http://storagenode:14002/api/" + path)
    return response.json()
   
  def get_data(self):
    return self.call_api("dashboard")['data']

  def get_satellites(self):
    satellites = []
    for item in self.data['satellites']:
      satellites.append(item['id'])
    return satellites

  def get_sat_data(self):
    array = {}
    for sat in self.satellites:
      data = self.call_api("satellite/" + sat)['data']
      array.update({sat : data})
    return array  

  def collect(self):
    for key in ['nodeID','wallet','lastPinged','lastPingFromID','lastPingFromAddress','upToDate']:
      value = str(self.data[key])
      metric = InfoMetricFamily("storj_" + key, "Storj " + key, value={key : value})
      #metric.add_metric({key : value})
      yield metric

    for array in ['diskSpace','bandwidth']:
      for key in ['used','available']:
        value = self.data[array][key]
        metric = GaugeMetricFamily("storj_" + array + "_" + key, "Storj " + array + " " + key, value=value)
        yield metric

    for array in ['audit','uptime']:
      for key in list(self.sat_data.values())[0][array]:
        metric = GaugeMetricFamily("storj_sat_" + array + "_" + key, "Storj satellite " + key,labels=["satellite"])
        for sat in self.satellites:
          value = self.sat_data[sat][array][key]
          metric.add_metric([sat], value)
        yield metric
    
    for key in ['storageSummary','bandwidthSummary']:
      metric = GaugeMetricFamily("storj_sat_" + key, "Storj satellite " + key,labels=["satellite"])
      for sat in self.satellites:
        value = self.sat_data[sat][key]
        metric.add_metric([sat], value)
      yield metric

if __name__ == "__main__":
  REGISTRY.register(StorjCollector())
  start_http_server(9651)
  while True: time.sleep(1)
