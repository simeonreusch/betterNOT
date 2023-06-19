#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import getpass
import logging

import keyring
import requests
from betternot import fritz

logger = logging.getLogger()


def get_finding_chart(ztf_id: str):
    url = f"/sources/{ztf_id}/finder"
    data = {"imsize": 2}
    response = fritz.api(method="get", url=url, data=data)

    print(f"HTTP code: {response.status_code}, {response.reason}")
    if response.status_code in (200, 400):
        print(response.text)
        # print(f"JSON response: {response.json()}")
