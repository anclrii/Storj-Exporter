import pytest

from storj_exporter.collectors import StorjCollector, NodeCollector, SatCollector
from storj_exporter.collectors import PayoutCollector
from prometheus_client.exposition import generate_latest


@pytest.fixture(name="list_of_dicts")
def fixture_mock_get_satellite():
    return [
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
    ]

@pytest.fixture
def gauge_dict():
    return {'used': 42, 'available': 10, 'trash': 15, 'overused': 0}


class TestStorjCollector:
    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize("mock_get_sno",
                             [("success"), ("missingkeys"), ("timeout")],
                             indirect=True)
    def test_collect_metric_map(self, client):
        node_metric_map = NodeCollector(client)._gen_node_metric_map()
        result = StorjCollector(client)._collect_metric_map(node_metric_map)
        res_list = list(result)
        assert len(res_list) == len(NodeCollector(client)._gen_node_metric_map())

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize("mock_get_sno, expected_samples",
                             [("success", 3), ("missingkeys", 0), ("timeout", 0)],
                             indirect=['mock_get_sno'])
    def test_add_metric_data(self, client, expected_samples):
        node_metric_map = NodeCollector(client)._gen_node_metric_map()
        metric = node_metric_map['storj_total_diskspace']
        result = StorjCollector(client)._add_metric_data(metric)
        assert result.name == 'storj_total_diskspace'
        assert result.documentation == 'Storj total diskspace metrics'
        assert len(result.samples) == expected_samples

    @pytest.mark.parametrize("key, expected_labels, expected_value", [
        ("used", 1, 42),
        ("missing", 0, 0.0)])
    def test_get_metric_values(self, gauge_dict, client, key, expected_labels,
                               expected_value):
        labels_list, value = StorjCollector._get_metric_values(
            StorjCollector(client), gauge_dict, 'gauge', key)
        assert len(labels_list) == expected_labels
        assert value == expected_value

    @pytest.mark.parametrize("key, expected_value", [
        ("used", 42),
        ("missing", 0.0)])
    def test_get_metric_value(self, gauge_dict, key, expected_value):
        value = StorjCollector._get_metric_value(gauge_dict, 'gauge', key)
        assert value == expected_value

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
    @pytest.mark.parametrize("mock_get_sno, expected_len",
                             [("success", 13), ("notfound", 0), ("timeout", 0)],
                             indirect=['mock_get_sno'])
    def test_refresh_data(self, client, expected_len):
        collector = NodeCollector(client)
        collector._refresh_data()
        assert isinstance(collector._node, dict)
        assert len(list(collector._node)) == expected_len

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize(
        "mock_get_sno, expected_metrics, expected_samples",
        [
            ("success", 3, 7),
            ("wrongtext", 3, 0),
            ("missingkeys", 3, 0),
            ("notfound", 3, 0),
            ("timeout", 3, 0)
        ],
        indirect=['mock_get_sno'])
    def test_collect(self, client, expected_metrics, expected_samples):
        collector = NodeCollector(client)
        result = collector.collect()
        res_list = list(result)
        assert len(res_list) == len(collector._gen_node_metric_map())
        assert len(res_list[0].samples) == expected_samples

    def test_gen_node_metric_map(self, client):
        node_metric_map = NodeCollector(client)._gen_node_metric_map()
        assert isinstance(node_metric_map, dict)
        assert len(node_metric_map) == len(NodeCollector(client)._gen_node_metric_map())

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize(
        "mock_get_sno, expected_len",
        [
            ("success", 18),
            ("wrongtext", 6),
            ("missingkeys", 6),
            ("notfound", 6),
            ("timeout", 6)
        ],
        indirect=['mock_get_sno'])
    def test_exposition(self, client, expected_len):
        collector = NodeCollector(client)
        output = generate_latest(collector)
        assert isinstance(output, bytes)
        assert len(output.splitlines()) == expected_len


class TestSatCollector:
    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize("mock_get_sno, expected_len",
                             [("success", 13), ("notfound", 0), ("timeout", 0)],
                             indirect=['mock_get_sno'])
    def test_refresh_data(self, client, expected_len):
        collector = SatCollector(client)
        collector._refresh_data()
        assert isinstance(collector._node, dict)
        assert len(list(collector._node)) == expected_len

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.usefixtures("mock_get_satellite")
    @pytest.mark.parametrize(
        "mock_get_sno, mock_get_satellite, expected_metrics",
        [
            ("success", "success", 10),
            ("success", "wrongtext", 10),
            ("success", "missingkeys", 10),
            ("success", "notfound", 10),
            ("success", "timeout", 10),
            ("missingkeys", "success", 0),
            ("timeout", "success", 0),
            ("timeout", "timeout", 0),
        ],
        indirect=['mock_get_sno', 'mock_get_satellite'])
    def test_collect(self, client, expected_metrics):
        collector = SatCollector(client)
        result = collector.collect()
        res_list = list(result)
        assert len(res_list) >= expected_metrics

    def test_gen_sat_metric_map(self, client):
        collector = SatCollector(client)
        collector._refresh_data()
        _sat_data = collector.client.satellite('id')
        sat_metric_map = collector._gen_sat_metric_map(_sat_data, 'id', 'url')
        assert isinstance(sat_metric_map, dict)
        assert sat_metric_map

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.usefixtures("mock_get_satellite")
    @pytest.mark.parametrize(
        "mock_get_sno, mock_get_satellite, expected_len",
        [
            ("success", "success", 10),
            ("success", "wrongtext", 10),
            ("success", "missingkeys", 10),
            ("success", "notfound", 10),
            ("success", "timeout", 10),
            ("missingkeys", "success", 0),
            ("timeout", "success", 0),
            ("timeout", "timeout", 0),
        ],
        indirect=['mock_get_sno', 'mock_get_satellite'])
    def test_exposition(self, client, expected_len):
        collector = SatCollector(client)
        output = generate_latest(collector)
        assert isinstance(output, bytes)
        assert len(output.splitlines()) >= expected_len


class TestPayoutCollector:
    @pytest.mark.usefixtures("mock_get_payout")
    @pytest.mark.parametrize("mock_get_payout, expected_len",
                             [("success", 9), ("notfound", 0), ("timeout", 0)],
                             indirect=['mock_get_payout'])
    def test_refresh_data(self, client, expected_len):
        collector = PayoutCollector(client)
        collector._refresh_data()
        assert isinstance(collector._payout, dict)
        assert len(list(collector._payout)) == expected_len

    @pytest.mark.usefixtures("mock_get_payout")
    @pytest.mark.parametrize(
        "mock_get_payout, expected_metrics, expected_samples",
        [
            ("success", 3, 9),
            ("wrongtext", 3, 0),
            ("missingkeys", 3, 0),
            ("notfound", 3, 0),
            ("timeout", 3, 0)
        ],
        indirect=['mock_get_payout'])
    def test_collect(self, client, expected_metrics, expected_samples):
        collector = PayoutCollector(client)
        result = collector.collect()
        res_list = list(result)
        assert len(res_list) == len(collector._gen_payout_metric_map())
        assert len(res_list[0].samples) == expected_samples

    def test_gen_payout_metric_map(self, client):
        payout_metric_map = PayoutCollector(client)._gen_payout_metric_map()
        assert isinstance(payout_metric_map, dict)
        assert payout_metric_map

    @pytest.mark.usefixtures("mock_get_payout")
    @pytest.mark.parametrize(
        "mock_get_payout, expected_len",
        [
            ("success", 11),
            ("wrongtext", 2),
            ("missingkeys", 2),
            ("notfound", 2),
            ("timeout", 2)
        ],
        indirect=['mock_get_payout'])
    def test_exposition(self, client, expected_len):
        collector = PayoutCollector(client)
        output = generate_latest(collector)
        assert isinstance(output, bytes)
        assert len(output.splitlines()) == expected_len
