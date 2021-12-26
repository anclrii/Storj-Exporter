from typing import Generator
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
    def test_get(self, client):
        response = client._get('sno/')
        assert response != {}
        assert response is not None
        assert isinstance(response, dict)

    @pytest.mark.usefixtures("mock_get_sno")
    def test_get_wrong_path(self, client):
        response = client._get('wrong/path/')
        assert response is None

    @pytest.mark.usefixtures("mock_get_sno")
    def test_node(self, client):
        response = client.node()
        assert response != {}
        assert response is not None
        assert isinstance(response, dict)

    def test_node_fail(self, client):
        response = client.node()
        assert response is None

    @pytest.mark.usefixtures("mock_get_sno")
    def test_node_data_keys(self, client):
        """
        Test that the keys are present in api node response.
        """
        n = client.node()
        assert n.keys() >= {'nodeID', 'wallet', 'lastPinged', 'upToDate', 'version',
                            'allowedVersion', 'startedAt'}
        assert n['diskSpace'].keys() >= {'used', 'available', 'trash', 'overused'}
        assert n['bandwidth'].keys() >= {'used', 'available'}
        assert n['satellites'][0].keys() >= {'id', 'url', 'disqualified', 'suspended'}
        assert n['satellites'][0].keys() >= {'id', 'url', 'disqualified', 'suspended'}

    @pytest.mark.usefixtures("mock_get_payout")
    def test_payout(self, client):
        response = client.payout()
        assert response != {}
        assert response is not None
        assert isinstance(response, dict)

    def test_payout_fail(self, client):
        response = client.payout()
        assert response is None

    @pytest.mark.usefixtures("mock_get_payout")
    def test_payout_data_keys(self, client):
        """
        Test that the keys are present in api payout response.
        """
        p = client.payout()
        assert p['currentMonth'].keys() >= {'payout', 'held'}

    @pytest.mark.usefixtures("mock_get_satellite")
    def test_satellite(self, client):
        response = client.satellite(pytest.sat_id)
        assert response != {}
        assert response is not None
        assert isinstance(response, dict)

    def test_satellite_fail(self, client):
        response = client.satellite(pytest.sat_id)
        assert response is None

    @pytest.mark.usefixtures("mock_get_satellite")
    def test_satellite_data_keys(self, client):
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

    @pytest.mark.usefixtures("mock_get_sno")
    def test_sat_id_generator(self, client):
        result = client.sat_id_generator()
        res_list = list(result)
        assert isinstance(result, Generator)
        assert len(res_list) > 1
        assert pytest.sat_id in res_list

    def test_sat_id_generator_fail(self, client):
        result = client.sat_id_generator()
        res_list = list(result)
        assert isinstance(result, Generator)
        assert len(res_list) == 0

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.usefixtures("mock_get_satellite")
    def test_sat_data_generator(self, client):
        result = client.sat_data_generator()
        res_list = list(result)
        assert isinstance(result, Generator)
        assert len(res_list) > 1
        assert res_list[0]['id'] == pytest.sat_id

    def test_sat_data_generator_fail(self, client):
        result = client.sat_data_generator()
        res_list = list(result)
        assert isinstance(result, Generator)
        assert len(res_list) == 0
