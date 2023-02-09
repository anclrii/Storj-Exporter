import pytest
from storj_exporter.collectors import StorjCollector, NodeCollector, SatCollector
from storj_exporter.collectors import PayoutCollector
from prometheus_client.exposition import generate_latest


@pytest.fixture
def gauge_dict():
    return {'used': 42, 'available': 10, 'trash': 15, 'overused': 0}


class TestStorjCollector:
    def test_init(self, client):
        collector = StorjCollector(client)
        assert collector.client == client


class TestNodeCollector:
    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize("mock_get_sno, expected_len",
                             [("success", 5), ("notfound", 0), ("timeout", 0)],
                             indirect=['mock_get_sno'])
    def test_refresh_data(self, client, expected_len):
        collector = NodeCollector(client)
        collector._refresh_data()
        assert isinstance(collector._node, dict)
        assert len(list(collector._node)) >= expected_len

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize(
        "mock_get_sno, expected_samples",
        [
            ("success", 1),
            ("wrongtext", 0),
            ("missingkeys", 0),
            ("notfound", 0),
            ("timeout", 0)
        ],
        indirect=['mock_get_sno'])
    def test_collect(self, client, expected_samples):
        collector = NodeCollector(client)
        result = collector.collect()
        res_list = list(result)
        assert len(res_list) == 3
        for metric in res_list:
            assert len(metric.samples) >= expected_samples

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize("mock_get_sno",
                             [("success"), ("notfound"), ("timeout")],
                             indirect=['mock_get_sno'])
    def test_get_metric_template_map(self, client):
        _metric_template_map = NodeCollector(client)._get_metric_template_map()
        assert isinstance(_metric_template_map, list)
        assert len(_metric_template_map) == 3

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize(
        "mock_get_sno, expected_len",
        [
            ("success", 10),
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
        assert len(output.splitlines()) >= expected_len


class TestSatCollector:
    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize("mock_get_sno, expected_len",
                             [("success", 14), ("notfound", 0), ("timeout", 0)],
                             indirect=['mock_get_sno'])
    def test_refresh_data(self, client, expected_len):
        collector = SatCollector(client)
        collector._refresh_data()
        assert isinstance(collector._node, dict)
        assert len(list(collector._node)) == expected_len

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.usefixtures("mock_get_satellite")
    @pytest.mark.parametrize(
        "mock_get_sno, mock_get_satellite, expected_samples",
        [
            ("success", "success", 1),
            ("success", "wrongtext", 0),
            ("success", "missingkeys", 0),
            ("success", "notfound", 0),
            ("success", "timeout", 0),
            ("missingkeys", "success", 0),
            ("timeout", "success", 0),
            ("timeout", "timeout", 0),
        ],
        indirect=['mock_get_sno', 'mock_get_satellite'])
    def test_collect(self, client, expected_samples):
        collector = SatCollector(client)
        result = collector.collect()
        res_list = list(result)
        assert len(res_list) == 5
        for metric in res_list:
            assert len(metric.samples) >= expected_samples

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.usefixtures("mock_get_satellite")
    @pytest.mark.parametrize("mock_get_satellite",
                             [("success"), ("notfound"), ("timeout")],
                             indirect=['mock_get_satellite'])
    def test_gen_sat_metric_map(self, client):
        collector = SatCollector(client)
        _sat_data = collector.client.satellite('id')
        _metric_template_map = collector._get_metric_template_map(
            _sat_data, 'id', 'url')
        assert isinstance(_metric_template_map, list)
        assert _metric_template_map

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.usefixtures("mock_get_satellite")
    @pytest.mark.parametrize(
        "mock_get_sno, mock_get_satellite, expected_len",
        [
            ("success", "success", 7),
            ("success", "wrongtext", 7),
            ("success", "missingkeys", 7),
            ("success", "notfound", 7),
            ("success", "timeout", 7),
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
                             [("success", 3), ("notfound", 0), ("timeout", 0)],
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
            ("success", 3, 10),
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
        assert len(res_list) == 1
        assert len(res_list[0].samples) == expected_samples

    @pytest.mark.usefixtures("mock_get_payout")
    @pytest.mark.parametrize("mock_get_payout",
                             [("success"), ("notfound"), ("timeout")],
                             indirect=['mock_get_payout'])
    def test_gen_payout_metric_map(self, client):
        _metric_template_map = PayoutCollector(client)._get_metric_template_map()
        assert isinstance(_metric_template_map, list)
        assert len(_metric_template_map) == 1

    @pytest.mark.usefixtures("mock_get_payout")
    @pytest.mark.parametrize(
        "mock_get_payout, expected_len",
        [
            ("success", 12),
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
