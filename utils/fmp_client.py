#=====================================
# Financial Modeling Prep API Client
#=====================================

import requests

from config.config import (
    FMP_API_KEY,
    HEADERS,
    HTTP_TIMEOUT
)


def get_json(url, params=None):
    """
    Send GET request to FMP and return JSON.
    """

    if params is None:
        params = {}

    params["apikey"] = FMP_API_KEY

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=HTTP_TIMEOUT
    )

    response.raise_for_status()

    return response.json()