#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import requests

from betternot import credentials

FRITZ_TOKEN = credentials.get_password(service="fritz_api")
BASE_URL = "https://fritz.science/api"


def api(
    method: str, url: str, data: dict | None = None, stream: bool = False
) -> requests.Response:
    headers = {"Authorization": f"token {FRITZ_TOKEN}"}

    endpoint = BASE_URL + url
    response = requests.request(
        method=method, url=endpoint, json=data, headers=headers, stream=stream
    )
    return response


def radec(ztf_id: str):
    """
    Get RA and Dec of a source, specified by its ZTF-ID
    """
    response = api(method="get", url=f"/sources/{ztf_id}")

    if response.status_code in (200, 400):
        res = response.json()
        ra = res["data"].get("ra")
        dec = res["data"].get("dec")

        return (ra, dec)
