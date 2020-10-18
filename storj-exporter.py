import os
import time
import requests
import json
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily, REGISTRY

class StorjCollector(object):
  def __init__(self):
    self.data = None
    self.satellites = {}
    self.sat_data = {}
    self.storj_host_address = os.environ.get('STORJ_HOST_ADDRESS', '127.0.0.1')
    self.storj_api_port = os.environ.get('STORJ_API_PORT', '14002')
    self.baseurl = "http://" + self.storj_host_address + ":" + self.storj_api_port + "/"
    self.basepath = "api/" # 2do - move trailing snash to individual requests

  def call_api(self,path):
    response = None
    try:
      response=requests.get(url = self.baseurl + self.basepath + path)
      response=response.json()
    except:
      pass
    return response
   
  def get_data(self):
    self.data = self.call_api("sno/")

  def get_satellites(self):
    if self.data:
      for item in self.data['satellites']:
        self.satellites.update({item['id']: item})

  def get_sat_data(self):
    for sat, value in self.satellites.items():
      data = self.call_api("sno/satellite/" + value['id']) # ['data']
      data.update({'disqualified': 1}) if value['disqualified'] else data.update({'disqualified': 0})
      data.update({'suspended': 1}) if value['suspended'] else data.update({'suspended': 0})
      data.update({'url': value['url']})
      self.sat_data.update({sat : data})

  def add_iterable_metrics(self, keys, data, metric, labels = []):
    for key in keys:
      value = 0
      if data[key]:
        value = data[key]
      metric_labels = [key] + labels
      metric.add_metric(metric_labels, value)
    
  def add_day_sum_metrics(self, key, data, metric, labels = []):
    value=0
    if data:
      for day in data:
        value=value + day[key]
    metric_labels = [key] + labels
    metric.add_metric(metric_labels, value)
    
  def add_iterable_day_sum_metrics(self, keys, data, item, metric, labels = []):
    for key in keys:
      value=0
      if data:
        for day in data:
          value=value + day[item][key]
      metric_labels = [key] + labels
      metric.add_metric(metric_labels, value)
    
  def add_node_metrics(self):
    if self.data:
      for key in ['nodeID','wallet','lastPinged','upToDate','version','allowedVersion']:
        value = str(self.data[key])
        metric = InfoMetricFamily("storj_" + key, "Storj " + key, value={key : value})
        yield metric
      storj_total_diskspace = GaugeMetricFamily("storj_total_diskspace", "Storj total diskspace metrics", labels=["type"])
      storj_total_bandwidth = GaugeMetricFamily("storj_total_bandwidth", "Storj total bandwidth metrics", labels=["type"])
      self.add_iterable_metrics(['used','available'], self.data["diskSpace"], storj_total_diskspace)
      self.add_iterable_metrics(['used','available'], self.data["bandwidth"], storj_total_bandwidth)
      yield storj_total_diskspace
      yield storj_total_bandwidth

  def add_sat_metrics(self):
    if self.satellites:
      self.get_sat_data()
      storj_sat_summary               = GaugeMetricFamily("storj_sat_summary",        "Storj satellite summary metrics",                                  labels=["type", "satellite", "url"])    
      storj_sat_audit                 = GaugeMetricFamily("storj_sat_audit",          "Storj satellite audit metrics",                                    labels=["type", "satellite", "url"])
      storj_sat_uptime                = GaugeMetricFamily("storj_sat_uptime",         "Storj satellite uptime metrics",                                   labels=["type", "satellite", "url"])
      storj_sat_month_egress          = GaugeMetricFamily("storj_sat_month_egress",   "Storj satellite egress since current month start",                 labels=["type", "satellite", "url"])
      storj_sat_month_ingress         = GaugeMetricFamily("storj_sat_month_ingress",  "Storj satellite ingress since current month start",                labels=["type", "satellite", "url"])
      storj_sat_day_egress            = GaugeMetricFamily("storj_sat_day_egress",     "Storj satellite egress since current day start",                   labels=["type", "satellite", "url"])
      storj_sat_day_ingress           = GaugeMetricFamily("storj_sat_day_ingress",    "Storj satellite ingress since current day start",                  labels=["type", "satellite", "url"])
      storj_sat_day_storage           = GaugeMetricFamily("storj_sat_day_storage",    "Storj satellite data stored on disk since current day start",      labels=["type", "satellite", "url"])

      for sat in self.satellites:
        self.add_iterable_metrics(['storageSummary','bandwidthSummary','disqualified','suspended'], self.sat_data[sat], storj_sat_summary, [sat, self.sat_data[sat]['url'], self.sat_data[sat]['url']])
        self.add_iterable_metrics(list(self.sat_data.values())[0]["audit"], self.sat_data[sat]["audit"], storj_sat_audit, [sat, self.sat_data[sat]['url']])
        self.add_iterable_metrics(list(self.sat_data.values())[0]["uptime"], self.sat_data[sat]["uptime"], storj_sat_uptime, [sat, self.sat_data[sat]['url']])
        self.add_iterable_day_sum_metrics(['repair','audit','usage'], self.sat_data[sat]['bandwidthDaily'], "egress", storj_sat_month_egress, [sat, self.sat_data[sat]['url']])
        self.add_iterable_day_sum_metrics(['repair','usage'], self.sat_data[sat]['bandwidthDaily'], "ingress", storj_sat_month_ingress, [sat, self.sat_data[sat]['url']])
        if self.sat_data[sat]['bandwidthDaily']:
          self.add_iterable_metrics(['repair','audit','usage'], self.sat_data[sat]['bandwidthDaily'][-1]['egress'], storj_sat_day_egress, [sat, self.sat_data[sat]['url']])
          self.add_iterable_metrics(['repair','usage'], self.sat_data[sat]['bandwidthDaily'][-1]['ingress'], storj_sat_day_ingress, [sat, self.sat_data[sat]['url']])
        if self.sat_data[sat]['storageDaily']:
          storj_sat_day_storage.add_metric(["atRestTotal", sat, self.sat_data[sat]['url']], self.sat_data[sat]['storageDaily'][-1]['atRestTotal'])

      yield storj_sat_summary
      yield storj_sat_audit
      yield storj_sat_uptime
      yield storj_sat_month_egress
      yield storj_sat_month_ingress
      yield storj_sat_day_egress
      yield storj_sat_day_ingress
      yield storj_sat_day_storage

  def collect(self):
    self.get_data()
    yield from self.add_node_metrics()  
    self.get_satellites()
    yield from self.add_sat_metrics()

if __name__ == "__main__":
  storj_exporter_port = os.environ.get('STORJ_EXPORTER_PORT', '9651')
  REGISTRY.register(StorjCollector())
  start_http_server(int(storj_exporter_port))
  while True: time.sleep(1)