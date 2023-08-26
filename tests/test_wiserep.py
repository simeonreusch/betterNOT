#!/usr/bin/env python
# coding: utf-8

import logging
import os
import unittest
from pathlib import Path

from betternot.wiserep import Wiserep


class TestWiserep(unittest.TestCase):
    def setUp(self):
        logging.getLogger("betternot.wiserep").setLevel(logging.DEBUG)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def test_upload(self):
        self.logger.info("\n\n Testing WISeREP spectrum upload \n\n")

        testspec_path = (
            Path(__file__).parent.parent / "data" / "ZTF23aaawbsc_combined_3850.ascii"
        )

        wrep = Wiserep(
            ztf_id="ZTF23aaawbsc",
            spec_path=testspec_path,
            sandbox=True,
            quality="high",
        )

        res = wrep.res

        res_object = wrep.res["data"]["recieved_data"]["objects"][0]["iau_name"]
        res_success = wrep.res["id_message"]

        res_object_expected = "2023aew"
        res_success_expected = "OK"

        self.assertEqual(res_object, res_object_expected)
        self.assertEqual(res_success, res_success_expected)


if __name__ == "__main__":
    unittest.main()
