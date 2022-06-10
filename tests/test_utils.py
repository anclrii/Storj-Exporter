
import pytest
from storj_exporter import utils


@pytest.fixture(name="list_of_dicts")
def fixture_mock_get_satellite():
    return [
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
        {'egress': {'repair': 1, 'audit': 2, 'usage': 3}, 'key': 4},
    ]


class Testutils:
    def testsum_list_of_dicts(self, list_of_dicts):
        sum_dict = utils.sum_list_of_dicts(list_of_dicts, 'egress')
        assert sum_dict == {'repair': 3, 'audit': 6, 'usage': 9}
        sum_dict = utils.sum_list_of_dicts(list_of_dicts, 'test')
        assert sum_dict == {}
        sum_dict = utils.sum_list_of_dicts(list_of_dicts, 'test', None)
        assert sum_dict is None

    def testsafe_list_get(self):
        list = [0, 1, 2]
        assert utils.safe_list_get(list, 1) == 1
        assert utils.safe_list_get(list, 5) == {}
        assert utils.safe_list_get(list, 5, None) is None

    @pytest.mark.parametrize('value, expected', [
        (1, 1.0),
        (1.1, 1.1),
        (0, 0.0),
        (None, None),
        ('1.1', 1.1),
        ('None', None),
        ('test', None),
        ('', None),
        (True, 1.0),
        (False, 0.0),
        ([1.1], None)
    ])
    def test_to_float(self, value, expected):
        assert utils.to_float(value) == expected
