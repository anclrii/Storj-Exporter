import requests

class ApiClient(object):
    """
    Storagenode (Storj) api client.
    (https://github.com/storj/storj/blob/main/storagenode/console/consoleserver/server.go)
    """
    def __init__(self, base_url, path="/api/", timeout=10, retries=3):
        self._api_url = base_url + path
        self._timeout = timeout
        self._session = self._make_session(retries)

    def _make_session(self, retries):
        session = requests.Session()
        http_adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        session.mount('http://', http_adapter)
        session.mount('https://', http_adapter)
        return session

    def _get(self, endpoint, default=None):
        response = default
        try:
            url = self._api_url + endpoint
            response = self._session.get(url=url, timeout=self._timeout).json()
        except Exception:
            pass
        return response

    def node(self):
        return self._get('sno/', {})

    def payout(self):
        return self._get('sno/estimated-payout', {})

    def satellite(self, sat_id):
        return self._get('sno/satellite/' + sat_id, {})
