import pytest
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily
from storj_exporter.collectors import StorjCollector

@pytest.fixture(name="list_of_dicts")
def fixture_mock_get_satellite():
    return [
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
    ]

@pytest.fixture(name="node_metric_map")
def fixture_gen_node_metric_map(self):
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
            'dict': self._node(),
        },
        'storj_total_diskspace': {
            'metric_object': GaugeMetricFamily(
                name='storj_total_diskspace',
                documentation='Storj total diskspace metrics',
                labels=['type']
            ),
            'extra_labels': [],
            'dict_keys': ['used', 'available', 'trash'],
            'dict': self._node()['diskSpace'],
        },
        'storj_total_bandwidth': {
            'metric_object': GaugeMetricFamily(
                name='storj_total_bandwidth',
                documentation='Storj total bandwidth metrics',
                labels=['type']
            ),
            'extra_labels': [],
            'dict_keys': ['used', 'available'],
            'dict': self._node()['bandwidth'],
        },
    }
    return _metricMap

class TestStorjCollector:
    def test_collect_metric_map(self):
        assert True

    def test_sum_list_of_dicts_by_key(self, list_of_dicts):
        sum_dict = StorjCollector._sum_list_of_dicts_by_key(list_of_dicts, 'egress')
        assert sum_dict == {'repair': 3, 'audit': 6, 'usage': 9}
        sum_dict = StorjCollector._sum_list_of_dicts_by_key(list_of_dicts, 'test')
        assert sum_dict == {}
        sum_dict = StorjCollector._sum_list_of_dicts_by_key(list_of_dicts, 'test', None)
        assert sum_dict is None

    def test_safe_list_get(self):
        list = [0, 1, 2]
        assert StorjCollector._safe_list_get(list, 1) == 1
        assert StorjCollector._safe_list_get(list, 5) == {}
        assert StorjCollector._safe_list_get(list, 5, None) is None
