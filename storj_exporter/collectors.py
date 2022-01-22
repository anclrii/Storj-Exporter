from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily
from collections import Counter


class StorjCollector(object):
    def __init__(self, client):
        self.client = client
        self._refresh_data()

    def _refresh_data(self):
        pass

    def collect(self):
        pass

    def _collect_metric_map(self, metric_map):
        for metric in metric_map.values():
            yield self._add_metric_data(metric)

    def _add_metric_data(self, metric):
        dict = metric['dict']
        metric_object = metric['metric_object']
        dict_keys = metric['dict_keys']
        extra_labels = metric['extra_labels']
        if dict:
            for label_value in dict_keys:
                labels_list, value = self._get_metric_values(
                    dict, metric_object.type, label_value, extra_labels)
                metric_object.add_metric(labels_list, value)
            return metric_object

    def _get_metric_values(self, dict, metric_type, label_value, extra_labels=[]):
        labels_list = []
        value = 0.0
        if label_value in dict:
            labels_list = [label_value] + extra_labels
            value = self._get_metric_value(dict, metric_type, label_value)
        return labels_list, value

    @staticmethod
    def _get_metric_value(dict, metric_type, label_value):
        value = 0.0
        if metric_type == "info":
            value = {label_value: str(dict[label_value])}
        elif isinstance(dict.get(label_value, None), (int, float)):
            value = dict.get(label_value, None)
        return value

    @staticmethod
    def _sum_list_of_dicts(list, path, default={}):
        _counter = Counter()
        try:
            for i in list:
                _counter.update(i[path])
            return dict(_counter)
        except Exception:
            return default

    @staticmethod
    def _safe_list_get(list, idx, default={}):
        try:
            return list[idx]
        except Exception:
            return default


class NodeCollector(StorjCollector):
    def _refresh_data(self):
        self._node = self.client.node()

    def collect(self):
        self._refresh_data()
        _node_metric_map = self._gen_node_metric_map()
        yield from self._collect_metric_map(_node_metric_map)

    def _gen_node_metric_map(self):
        """
        considered these options also:
        * custom data structure object - doesn't seem to add much value compared to
          dictionary
        * extend *MetricFamily classes - seems like a bad idea for compatibility
        * multiple flat dictionaries with matching keys - seems more complicated
        """
        _diskSpace = self._node.get('diskSpace', None)
        _bandwidth = self._node.get('bandwidth', None)

        _metricMap = {
            'storj_node': {
                'metric_object': InfoMetricFamily(
                    name='storj_node',
                    documentation='Storj node info',
                    labels=['type']
                ),
                'extra_labels': [],
                'dict_keys': ['nodeID', 'wallet', 'lastPinged', 'upToDate', 'version',
                              'allowedVersion', 'startedAt'],
                'dict': self._node,
            },
            'storj_total_diskspace': {
                'metric_object': GaugeMetricFamily(
                    name='storj_total_diskspace',
                    documentation='Storj total diskspace metrics',
                    labels=['type']
                ),
                'extra_labels': [],
                'dict_keys': ['used', 'available', 'trash'],
                'dict': _diskSpace,
            },
            'storj_total_bandwidth': {
                'metric_object': GaugeMetricFamily(
                    name='storj_total_bandwidth',
                    documentation='Storj total bandwidth metrics',
                    labels=['type']
                ),
                'extra_labels': [],
                'dict_keys': ['used', 'available'],
                'dict': _bandwidth,
            },
        }
        return _metricMap


class SatCollector(StorjCollector):
    """
    TODO
    * currently we create metric object per sattelite. Would be good to create  metric
      object per metric and add metrics of each sat to same matric object.
     * potentially split _metricMap into 2 maps - metric object map and values map
     * iterate over sats and populate values map
     * iterate over metrics object map and add valuesof all sats to each object then
       yield
     * this would also work for node metrics to keep things consisten where each metric
       will only have one values map item
     """
    def _refresh_data(self):
        self._node = self.client.node()

    def collect(self):
        self._refresh_data()
        for satellite in self._node['satellites']:
            _sat_data = self.client.satellite(satellite['id'])
            _suspended = 1 if satellite['suspended'] else 0
            _disqualified = 1 if satellite['disqualified'] else 0
            _sat_data.update({'suspended': _suspended})
            _sat_data.update({'disqualified': _disqualified})
            _sat_metric_map = self._gen_sat_metric_map(
                _sat_data, satellite['id'], satellite['url'])
            yield from self._collect_metric_map(_sat_metric_map)

    def _gen_sat_metric_map(self, _sat_data, _sat_id, _sat_url):
        _month_ingress = self._sum_list_of_dicts(
            _sat_data.get('bandwidthDaily', {}), "ingress")
        _month_egress = self._sum_list_of_dicts(
            _sat_data.get('bandwidthDaily', {}), "egress")
        _day_bandwidth = self._safe_list_get(_sat_data.get('bandwidthDaily', [{}]), -1)
        _day_storage = self._safe_list_get(_sat_data.get('storageDaily', None), -1)
        _audits = _sat_data.get('audits', None)

        _metricMap = {
            'storj_sat_summary': {
                'metric_object': GaugeMetricFamily(
                    name='storj_sat_summary',
                    documentation='Storj satellite summary metrics',
                    labels=['type', 'satellite', 'url']
                ),
                'extra_labels': [_sat_id, _sat_url],
                'dict_keys': ['storageSummary', 'bandwidthSummary', 'egressSummary',
                              'ingressSummary', 'currentStorageUsed', 'disqualified',
                              'suspended'],
                'dict': _sat_data,
            },
            'storj_sat_audit': {
                'metric_object': GaugeMetricFamily(
                    name='storj_sat_audit',
                    documentation='Storj satellite audit metrics',
                    labels=['type', 'satellite', 'url']
                ),
                'extra_labels': [_sat_id, _sat_url],
                'dict_keys': ['auditScore', 'suspensionScore', 'onlineScore'],
                'dict': _audits,
            },
            'storj_sat_month_egress': {
                'metric_object': GaugeMetricFamily(
                    name='storj_sat_month_egress',
                    documentation='Storj satellite egress since current month start',
                    labels=['type', 'satellite', 'url']
                ),
                'extra_labels': [_sat_id, _sat_url],
                'dict_keys': ['repair', 'audit', 'usage'],
                'dict': _month_egress,
            },
            'storj_sat_month_ingress': {
                'metric_object': GaugeMetricFamily(
                    name='storj_sat_month_ingress',
                    documentation='Storj satellite ingress since current month start',
                    labels=['type', 'satellite', 'url']
                ),
                'extra_labels': [_sat_id, _sat_url],
                'dict_keys': ['repair', 'usage'],
                'dict': _month_ingress,
            },
            'storj_sat_day_egress': {
                'metric_object': GaugeMetricFamily(
                    name='storj_sat_day_egress',
                    documentation='Storj satellite egress since current day start',
                    labels=['type', 'satellite', 'url']
                ),
                'extra_labels': [_sat_id, _sat_url],
                'dict_keys': ['repair', 'audit', 'usage'],
                'dict': _day_bandwidth.get('egress', None),
            },
            'storj_sat_day_ingress': {
                'metric_object': GaugeMetricFamily(
                    name='storj_sat_day_ingress',
                    documentation='Storj satellite ingress since current day start',
                    labels=['type', 'satellite', 'url']
                ),
                'extra_labels': [_sat_id, _sat_url],
                'dict_keys': ['repair', 'usage'],
                'dict': _day_bandwidth.get('ingress', None),
            },
            'storj_sat_day_storage': {
                'metric_object': GaugeMetricFamily(
                    name='storj_sat_day_storage',
                    documentation='Storj satellite data stored on disk since current '
                                  'day start',
                    labels=['type', 'satellite', 'url']
                ),
                'extra_labels': [_sat_id, _sat_url],
                'dict_keys': ['atRestTotal'],
                'dict': _day_storage,
            },
        }
        return _metricMap


class PayoutCollector(StorjCollector):
    def _refresh_data(self):
        self._payout = self.client.payout().get('currentMonth', {})

    def collect(self):
        self._refresh_data()
        _payout_metric_map = self._gen_payout_metric_map()
        yield from self._collect_metric_map(_payout_metric_map)

    def _gen_payout_metric_map(self):
        _metricMap = {
            'storj_payout_currentMonth': {
                'metric_object': GaugeMetricFamily(
                    name='storj_payout_currentMonth',
                    documentation='Storj estimated payouts for current month',
                    labels=['type']
                ),
                'extra_labels': [],
                'dict_keys': ['egressBandwidth', 'egressBandwidthPayout',
                              'egressRepairAudit', 'egressRepairAuditPayout',
                              'diskSpace', 'diskSpacePayout', 'heldRate', 'payout',
                              'held'],
                'dict': self._payout,
            },
        }
        return _metricMap


def print_samples(registry):
    for metric in registry.collect():
        for s in metric.samples:
            print(s)


if __name__ == '__main__':
    from api_wrapper import ApiClient
    from prometheus_client.core import REGISTRY

    client = ApiClient('http://localhost:14007/')
    node_collector = NodeCollector(client)
    sat_collector = SatCollector(client)
    payout_collector = PayoutCollector(client)
    REGISTRY.register(node_collector)
    REGISTRY.register(sat_collector)
    REGISTRY.register(payout_collector)
    print_samples(REGISTRY)
