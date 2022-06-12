import requests
import logging
from requests.adapters import HTTPAdapter, Retry
from json.decoder import JSONDecodeError

logger = logging.getLogger(__name__)


class ApiClient(object):
    """
    Storagenode (Storj) api client.
    (https://github.com/storj/storj/blob/main/storagenode/console/consoleserver/server.go)
    """
    def __init__(self, base_url, path="/api/", timeout=10, retries=2, backoff_factor=1):
        self._api_url = base_url + path
        self._timeout = timeout
        self._retries = Retry(total=retries, backoff_factor=backoff_factor)
        self._session = self._make_session()

    def _make_session(self):
        session = requests.Session()
        http_adapter = HTTPAdapter(max_retries=self._retries)
        session.mount('http://', http_adapter)
        session.mount('https://', http_adapter)
        return session

    def _get(self, endpoint, default=None):
        response_json = default
        try:
            url = self._api_url + endpoint
            response = self._session.get(url=url, timeout=self._timeout)
            response.raise_for_status()
            response_json = response.json()
        except requests.exceptions.RequestException:
            logger.debug(f"Error while getting data from {url}")
            pass
        except JSONDecodeError:
            logger.debug(f"Failed to parse json response from {url}")
            pass
        else:
            logger.debug(f"Got response from {url}")
        return response_json

    def node(self):
        return self._get('sno/', {})

    def payout(self):
        return self._get('sno/estimated-payout', {})

    def satellite(self, sat_id):
        return self._get('sno/satellite/' + sat_id, {})
