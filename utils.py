import sys
import requests
import logbook
from urllib.parse import urlparse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
_logger = logbook.Logger(__name__)


def is_url(string: str):
    if not isinstance(string, str):
        string = str(string)

    return bool(urlparse(string).scheme)


def request_with_retries(url: str,
                         method: str = "POST",
                         data=None,
                         files=None,
                         retries: int = 3,
                         timeout_seconds: int = 10,
                         statuses_for_retries: tuple = (500, 502, 503, 504),
                         **kwargs):
    with requests.Session() as session:
        retries = Retry(total=retries,
                        status_forcelist=list(statuses_for_retries))
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        try:
            result = session.request(method=method, url=url, data=data, files=files, timeout=timeout_seconds, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            orig_exc_info = sys.exc_info()
            _logger.debug(f"Request has failed for url={url} method={method}, data={data}, exc_info={orig_exc_info}")
            raise e

    return result.content.decode("utf-8")
