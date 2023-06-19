#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import getpass
import logging
import shutil

import keyring
import requests
from betternot import fritz

logger = logging.getLogger()


def get_finding_chart(ztf_id: str):
    url = f"/sources/{ztf_id}/finder?imsize=5&type=png&num_offset_stars=0"
    response = fritz.api(method="get", url=url, stream=True)

    print(f"HTTP code: {response.status_code}, {response.reason}")
    if response.status_code in (200, 400):
        with open(f"{ztf_id}.png", "wb") as f:
            shutil.copyfileobj(response.raw, f)
