import json
import re
import pytest

from storj_exporter.api_wrapper import ApiClient
from storj_exporter.collectors import StorjCollector

@pytest.fixture(autouse=True)
def set_globals():
    pytest.storj_version = 'v1.37.1'
    pytest.base_url = 'http://storj-exporter.com'
    pytest.sat_id = '12tRQrMTWUWwzwGh18i7Fqs67kmdhH9t6aToeiwbo5mfS2rUmo'
    pytest.mock_path = f'tests/api_mock/{pytest.storj_version}'

@pytest.fixture(name="client")
def client():
    return ApiClient(pytest.base_url)

@pytest.fixture(name="storj_collector")
def storj_collector():
    return StorjCollector(client)

@pytest.fixture(name="mock_get_sno")
def fixture_mock_get_sno(requests_mock):
    with open(f'{pytest.mock_path}/sno.json', 'r') as f:
        payload = json.loads(f.read())
    requests_mock.get(url=f'{pytest.base_url}/api/sno/', json=payload)

@pytest.fixture(name="mock_get_payout")
def fixture_mock_get_payout(requests_mock):
    with open(f'{pytest.mock_path}/payout.json', 'r') as f:
        payload = json.loads(f.read())
    requests_mock.get(url=f'{pytest.base_url}/api/sno/estimated-payout', json=payload)

@pytest.fixture(name="mock_get_satellite")
def fixture_mock_get_satellite(requests_mock):
    matcher = re.compile(f'{pytest.base_url}/api/sno/satellite/')
    with open(f'{pytest.mock_path}/satellite.json', 'r') as f:
        payload = json.loads(f.read())
    requests_mock.get(url=matcher, json=payload)
