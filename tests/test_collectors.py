import pytest
from storj_exporter.collectors import StorjCollector

@pytest.fixture(name="list_of_dicts")
def fixture_mock_get_satellite():
    return [
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
    ]

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

