from typing import Generator
import requests
import pytest

from storj_exporter.api_wrapper import ApiClient

class TestApiClient:
    def test_make_session(self, client):
        assert isinstance(client._session, requests.Session)

    def test_default_attributes(self, client):
        assert client._api_url == f'{pytest.base_url}/api/'
        assert client._timeout == 10

    def test_custom_attributes(self):
        client = ApiClient(pytest.base_url, path='/testpath/', timeout=60)
        assert client._api_url == f'{pytest.base_url}/testpath/'
        assert client._timeout == 60

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
    def test_payout_data_keys(self, client):
        """
        Test that the keys are present in api payout response.
        """
        p = client.payout()
        assert p['currentMonth'].keys() >= {'payout', 'held'}

    @pytest.mark.usefixtures("mock_get_satellite")
    def test_satellite_data_keys(self, client):
        """
        Test that the keys are present in api satellite response.
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
        g = client.sat_id_generator()
        i = list(g)
        assert isinstance(g, Generator)
        assert len(i) > 1
        assert pytest.sat_id in i

    @pytest.mark.usefixtures("mock_get_sno")
    @pytest.mark.usefixtures("mock_get_satellite")
    def test_sat_data_generator(self, client):
        g = client.sat_data_generator()
        i = list(g)
        assert isinstance(g, Generator)
        assert len(i) > 1
        assert i[0]['id'] == pytest.sat_id
