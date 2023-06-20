#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import getpass
import logging
import shutil
from pathlib import Path

import keyring
import requests

from betternot import fritz, io

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_finding_chart(ztf_id: str):
    url = f"/sources/{ztf_id}/finder?imsize=5&type=png&num_offset_stars=0"

    logger.info(f"Issuing finding chart request for {ztf_id}")
    response = fritz.api(method="get", url=url, stream=True)

    if response.status_code in (200, 400):
        outpath = io.get_object_dir(ztf_id)

        with open(outpath / f"{ztf_id}_finder.png", "wb") as f:
            shutil.copyfileobj(response.raw, f)
        logger.info(
            f"Downloaded finding chart for {ztf_id} to {outpath / f'{ztf_id}_finder.png'}"
        )
