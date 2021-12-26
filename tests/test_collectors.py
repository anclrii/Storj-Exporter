import pytest
from typing import Generator

from storj_exporter.collectors import NodeCollector, StorjCollector

@pytest.fixture(name="list_of_dicts")
def fixture_mock_get_satellite():
    return [
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
    ]

@pytest.fixture(name="gauge_dict")
def fixture_gauge_dict():
    return {'used': 3498284766336, 'available': 3500000000000, 'trash': 1222393984,
            'overused': 0}

class TestStorjCollector:
    @pytest.mark.usefixtures("mock_get_sno")
    def test_collect_metric_map(self, client):
        node_metric_map = NodeCollector(client)._gen_node_metric_map()
        result = StorjCollector(client)._collect_metric_map(node_metric_map)
        res_list = list(result)
        assert isinstance(result, Generator)
        assert len(res_list) == 3

    def test_collect_metric_map_api_fail(self, client):
        node_metric_map = NodeCollector(client)._gen_node_metric_map()
        result = StorjCollector(client)._collect_metric_map(node_metric_map)
        res_list = list(result)
        assert isinstance(result, Generator)
        assert res_list == [None, None, None]

    @pytest.mark.usefixtures("mock_get_sno")
    def test_add_metric_data(self, client):
        node_metric_map = NodeCollector(client)._gen_node_metric_map()
        metric = node_metric_map['storj_total_diskspace']
        result = StorjCollector(client)._add_metric_data(metric)
        assert result.name == 'storj_total_diskspace'
        assert result.documentation == 'Storj total diskspace metrics'
        assert len(result.samples) == 3

    def test_add_metric_data_api_fail(self, client):
        node_metric_map = NodeCollector(client)._gen_node_metric_map()
        metric = node_metric_map['storj_total_diskspace']
        result = StorjCollector(client)._add_metric_data(metric)
        assert result is None

    @pytest.mark.usefixtures("gauge_dict")
    def test_get_metric_values(self, client, gauge_dict):
        labels_list, value = StorjCollector._get_metric_values(
            StorjCollector(client), gauge_dict, 'gauge', 'used')
        assert labels_list == ['used']
        assert value == 3498284766336

    @pytest.mark.usefixtures("gauge_dict")
    def test_get_metric_value(self, gauge_dict):
        value = StorjCollector._get_metric_value(gauge_dict, 'gauge', 'used')
        assert value == 3498284766336

    def test_sum_list_of_dicts(self, list_of_dicts):
        sum_dict = StorjCollector._sum_list_of_dicts(list_of_dicts, 'egress')
        assert sum_dict == {'repair': 3, 'audit': 6, 'usage': 9}
        sum_dict = StorjCollector._sum_list_of_dicts(list_of_dicts, 'test')
        assert sum_dict == {}
        sum_dict = StorjCollector._sum_list_of_dicts(list_of_dicts, 'test', None)
        assert sum_dict is None

    def test_safe_list_get(self):
        list = [0, 1, 2]
        assert StorjCollector._safe_list_get(list, 1) == 1
        assert StorjCollector._safe_list_get(list, 5) == {}
        assert StorjCollector._safe_list_get(list, 5, None) is None


# class TestNodeCollector:
