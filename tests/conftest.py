import json
import re
import pytest
import requests
from storj_exporter.api_wrapper import ApiClient
from storj_exporter.collectors import StorjCollector


@pytest.fixture(autouse=True)
def set_globals():
    pytest.storj_version = 'v1.71.2'
    pytest.base_url = 'http://storj-exporter.com'
    pytest.sat_id = '12tRQrMTWUWwzwGh18i7Fqs67kmdhH9t6aToeiwbo5mfS2rUmo'
    pytest.mock_path = f'tests/api_mock/{pytest.storj_version}'

@pytest.fixture
def client():
    return ApiClient(pytest.base_url)

@pytest.fixture
def storj_collector():
    return StorjCollector(client)

@pytest.fixture(params=["success"])
def mock_get_sno(requests_mock, request):
    url_path = '/api/sno/'
    if request.param == "success":
        with open(f'{pytest.mock_path}/sno.json', 'r') as f:
            payload = json.loads(f.read())
        requests_mock.get(url=url_path, json=payload, status_code=200)
    elif request.param == "missingkeys":
        payload = {'k1': 'v1', 'k2': 'v2', 'satellites': [
                   {"id": "12tRQrMT", 'k2': None},
                   {'k1': 'v1', 'k2': None},
                   {},
                   None]}
        requests_mock.get(url=url_path, json=payload, status_code=200)
    elif request.param == "wrongtext":
        requests_mock.get(url=url_path, text="Wrong", status_code=300)
    elif request.param == "notfound":
        requests_mock.get(url=url_path, text="Not found", status_code=404)
    elif request.param == "timeout":
        requests_mock.get(url=url_path, exc=requests.exceptions.ConnectTimeout)

@pytest.fixture(params=["success"])
def mock_get_payout(requests_mock, request):
    url_path = '/api/sno/estimated-payout'
    if request.param == "success":
        with open(f'{pytest.mock_path}/payout.json', 'r') as f:
            payload = json.loads(f.read())
        requests_mock.get(url=url_path, json=payload, status_code=200)
    elif request.param == "missingkeys":
        payload = {'k1': 'v1', 'k2': None}
        requests_mock.get(url=url_path, json=payload, status_code=200)
    elif request.param == "wrongtext":
        requests_mock.get(url=url_path, text="Wrong", status_code=300)
    elif request.param == "notfound":
        requests_mock.get(url=url_path, text="Not found", status_code=404)
    elif request.param == "timeout":
        requests_mock.get(url=url_path, exc=requests.exceptions.ConnectTimeout)

@pytest.fixture(params=["success"])
def mock_get_satellite(requests_mock, request):
    url_path = re.compile(r'/api/sno/satellite/(.*)')
    if request.param == "success":
        with open(f'{pytest.mock_path}/satellite.json', 'r') as f:
            payload = json.loads(f.read())
        requests_mock.get(url=url_path, json=payload, status_code=200)
    elif request.param == "missingkeys":
        payload = {'k1': 'v1', 'k2': None}
        requests_mock.get(url=url_path, json=payload, status_code=200)
    elif request.param == "wrongtext":
        requests_mock.get(url=url_path, text="Wrong", status_code=300)
    elif request.param == "notfound":
        requests_mock.get(url=url_path, text="Not found", status_code=404)
    elif request.param == "timeout":
        requests_mock.get(url=url_path, exc=requests.exceptions.ConnectTimeout)

@pytest.fixture
def mock_returns_none(requests_mock):
    matcher = re.compile(f'{pytest.base_url}/api/')
    requests_mock.get(url=matcher, json=None)
