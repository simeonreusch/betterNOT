#!/usr/bin/env python
# coding: utf-8

import logging
import os
import unittest
from pathlib import Path

from astropy.time import Time  # type: ignore
from betternot import fritz
from betternot.findingchart import get_finding_chart
from betternot.observability import Observability
from betternot.wiserep import Wiserep


class TestWiserep(unittest.TestCase):
    def setUp(self):
        logging.getLogger("betternot.observability").setLevel(logging.DEBUG)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def test_obsprep(self):
        self.logger.info("\n\n Testing preparing a NOT observation\n\n")
        from requests import get

        date = "2023-08-26"
        ztf_ids = ["ZTF23aalftvv"]

        obs = Observability(ztf_ids=ztf_ids, date=date, site="not")
        obs.plot_standards()
        obs.plot_targets()
        get_finding_chart(ztf_id=ztf_ids[0], date=date)
        obs.print_info()

        obs_dict = obs.target_dict[ztf_ids[0]]
        obs_mjd = obs_dict["mjd"]
        now = Time.now().mjd
        days_ago = now - obs_mjd
        mag = obs_dict["mag"]
        band = obs_dict["band"]

        info_expected = f"-------------------------------------------\nZTF23aalftvv\nztf23aalftvv\nRA: 17:14:08.53728\nDec: +81:04:29.39952\n{mag:.2f} mag {days_ago:.0f} days ago in the {band} filter\n-------------------------------------------\n"

        self.assertEqual(obs.info, info_expected)


if __name__ == "__main__":
    unittest.main()
