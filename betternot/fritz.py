#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import backoff  # type: ignore
import requests

from betternot import credentials

FRITZ_TOKEN = credentials.get_password(service="fritz_api")
BASE_URL = "https://fritz.science/api"


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_time=600,
)
def api(
    method: str, url: str, data: dict | None = None, stream: bool = False
) -> requests.Response:
    """
    Basic API request method
    """
    headers = {"Authorization": f"token {FRITZ_TOKEN}"}

    endpoint = BASE_URL + url
    response = requests.request(
        method=method, url=endpoint, json=data, headers=headers, stream=stream
    )

    if response.status_code != 200:
        raise requests.exceptions.RequestException

    return response


def radec(ztf_id: str):
    """
    Get RA and Dec of a source, specified by its ZTF-ID
    """
    response = api(method="get", url=f"/sources/{ztf_id}")

    res = response.json()
    ra = res["data"].get("ra")
    dec = res["data"].get("dec")

    return (ra, dec)
