import requests
import pytest
from storj_exporter.api_wrapper import ApiClient


class TestApiClient:
    def test_init_default_attributes(self, client):
        assert isinstance(client._session, requests.Session)
        assert client._api_url == f'{pytest.base_url}/api/'
        assert client._timeout == 10

    def test_init_custom_attributes(self):
        client = ApiClient(pytest.base_url, path='/testpath/', timeout=60)
        assert client._api_url == f'{pytest.base_url}/testpath/'
        assert client._timeout == 60

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize(
        "mock_get_sno, expected_result, res_type",
        [
            ("success", True, dict),
            ("wrongtext", False, type(None)),
            ("missingkeys", True, dict),
            ("notfound", False, type(None)),
            ("timeout", False, type(None))
        ],
        indirect=['mock_get_sno'])
    def test_get(self, client, expected_result, res_type):
        response = client._get('sno/')
        assert isinstance(response, res_type)
        result = True if response else False
        assert result == expected_result
        if result is False:
            assert response is None

    def test_get_wrong_path(self, client):
        response = client._get('wrong/path/')
        assert response is None

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.parametrize(
        "mock_get_sno, expected_result, res_type",
        [
            ("success", True, dict),
            ("wrongtext", False, dict),
            ("missingkeys", True, dict),
            ("notfound", False, dict),
            ("timeout", False, dict)
        ],
        indirect=['mock_get_sno'])
    def test_node(self, client, expected_result, res_type):
        response = client.node()
        assert isinstance(response, res_type)
        result = True if response else False
        assert result == expected_result
        if result is False:
            assert response == {}

    @pytest.mark.usefixtures("mock_get_payout")
    @pytest.mark.parametrize(
        "mock_get_payout, expected_result, res_type",
        [
            ("success", True, dict),
            ("wrongtext", False, dict),
            ("missingkeys", True, dict),
            ("notfound", False, dict),
            ("timeout", False, dict)
        ],
        indirect=['mock_get_payout'])
    def test_payout(self, client, expected_result, res_type):
        response = client.payout()
        assert isinstance(response, res_type)
        result = True if response else False
        assert result == expected_result
        if result is False:
            assert response == {}

    @pytest.mark.usefixtures("mock_get_satellite")
    @pytest.mark.parametrize(
        "mock_get_satellite, expected_result, res_type",
        [
            ("success", True, dict),
            ("wrongtext", False, dict),
            ("missingkeys", True, dict),
            ("notfound", False, dict),
            ("timeout", False, dict)
        ],
        indirect=['mock_get_satellite'])
    def test_satellite(self, client, expected_result, res_type):
        response = client.satellite(pytest.sat_id)
        assert isinstance(response, res_type)
        result = True if response else False
        assert result == expected_result
        if result is False:
            assert response == {}


class TestApiClientKeys:
    @pytest.mark.usefixtures("mock_get_sno")
    def test_node_keys(self, client):
        """
        Test that the keys are present in api node response.
        """
        n = client.node()
        assert n.keys() >= {'nodeID', 'wallet', 'lastPinged', 'upToDate', 'version',
                            'allowedVersion', 'startedAt', 'quicStatus'}
        assert n['diskSpace'].keys() >= {'used', 'available', 'trash', 'overused'}
        assert n['bandwidth'].keys() >= {'used', 'available'}
        assert n['satellites'][0].keys() >= {'id', 'url', 'disqualified', 'suspended'}
        assert n['satellites'][0].keys() >= {'id', 'url', 'disqualified', 'suspended'}

    @pytest.mark.usefixtures("mock_get_payout")
    def test_payout_keys(self, client):
        """
        Test that the keys are present in api payout response.
        """
        p = client.payout()
        assert p['currentMonth'].keys() >= {'payout', 'held'}

    @pytest.mark.usefixtures("mock_get_satellite")
    def test_satellite_keys(self, client):
        """
        Test that the keys are present in satellite api response.
        """
        s = client.satellite(pytest.sat_id)
        assert s.keys() >= {'storageSummary', 'bandwidthSummary', 'egressSummary',
                            'ingressSummary', 'currentStorageUsed'}
        assert s['audits'].keys() >= {'auditScore', 'suspensionScore', 'onlineScore',
                                      'satelliteName'}
        assert s['storageDaily'][0].keys() >= {'atRestTotal'}
        assert s['bandwidthDaily'][0]['ingress'].keys() >= {'repair', 'usage'}
        assert s['bandwidthDaily'][0]['egress'].keys() >= {'repair', 'audit', 'usage'}
