import pytest
from typing import Generator

from storj_exporter.collectors import StorjCollector, NodeCollector, SatCollector
from storj_exporter.collectors import PayoutCollector

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
    def test_get_metric_values_missing(self, client, gauge_dict):
        labels_list, value = StorjCollector._get_metric_values(
            StorjCollector(client), gauge_dict, 'gauge', 'missing')
        assert labels_list == []
        assert value == 0.0

    @pytest.mark.usefixtures("gauge_dict")
    def test_get_metric_value(self, gauge_dict):
        value = StorjCollector._get_metric_value(gauge_dict, 'gauge', 'used')
        assert value == 3498284766336

    @pytest.mark.usefixtures("gauge_dict")
    def test_get_metric_value_missing(self, gauge_dict):
        value = StorjCollector._get_metric_value(gauge_dict, 'gauge', 'missing')
        assert value == 0.0

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


class TestNodeCollector:
    @pytest.mark.usefixtures("mock_get_sno")
    def test_refresh_data(self, client):
        collector = NodeCollector(client)
        collector._refresh_data()
        assert isinstance(collector._node, dict)
        assert collector._node

    @pytest.mark.usefixtures("mock_get_sno")
    def test_collect(self, client):
        collector = NodeCollector(client)
        g = collector.collect()
        assert isinstance(g, Generator)
        assert len(list(g)) == len(collector._gen_node_metric_map())

    @pytest.mark.usefixtures("mock_get_sno")
    def test_gen_node_metric_map(self, client):
        node_metric_map = NodeCollector(client)._gen_node_metric_map()
        assert isinstance(node_metric_map, dict)
        assert node_metric_map


class TestSatCollector:
    @pytest.mark.usefixtures("mock_get_sno")
    def test_refresh_data(self, client):
        collector = SatCollector(client)
        collector._refresh_data()
        assert isinstance(collector._node, dict)
        assert collector._node

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.usefixtures("mock_get_satellite")
    def test_collect(self, client):
        collector = SatCollector(client)
        g = collector.collect()
        assert isinstance(g, Generator)

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.usefixtures("mock_get_satellite")
    def test_gen_sat_metric_map(self, client):
        collector = SatCollector(client)
        collector._refresh_data()
        _sat_data = collector.client.satellite('id')
        sat_metric_map = collector._gen_sat_metric_map(_sat_data, 'id', 'url')
        assert isinstance(sat_metric_map, dict)
        assert sat_metric_map

    @pytest.mark.usefixtures("mock_get_sno")
    # @pytest.mark.usefixtures("mock_get_satellite")
    def test_gen_sat_metric_map_failed(self, client):
        collector = SatCollector(client)
        collector._refresh_data()
        _sat_data = collector.client.satellite('id')
        sat_metric_map = collector._gen_sat_metric_map(_sat_data, 'id', 'url')
        assert isinstance(sat_metric_map, dict)
        assert sat_metric_map


class TestPayoutCollector:
    @pytest.mark.usefixtures("mock_get_payout")
    def test_refresh_data(self, client):
        collector = PayoutCollector(client)
        collector._refresh_data()
        assert isinstance(collector._payout, dict)
        assert collector._payout

    @pytest.mark.usefixtures("mock_get_payout")
    def test_collect(self, client):
        collector = PayoutCollector(client)
        g = collector.collect()
        assert isinstance(g, Generator)
        assert len(list(g)) == len(collector._gen_payout_metric_map())

    @pytest.mark.usefixtures("mock_get_sno")
    def test_gen_payout_metric_map(self, client):
        payout_metric_map = PayoutCollector(client)._gen_payout_metric_map()
        assert isinstance(payout_metric_map, dict)
        assert payout_metric_map
