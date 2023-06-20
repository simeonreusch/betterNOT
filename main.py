#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import argparse
import logging

from betternot import fritz
from betternot.findingchart import get_finding_chart
from betternot.observability import Observability
from betternot.utils import is_ztf_name

transient = "ZTF19aatubsj"

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger("betternot.findingchart").setLevel(logging.INFO)


def run():
    parser = argparse.ArgumentParser(description="Various NOT tools")
    parser.add_argument(
        "name",
        type=str,
        help='Provide a ZTF name (e.g. "ZTF19aaelulu") or a .txt-file containing a list of ZTF names',
    )
    # parser.add_argument(
    #     "-finding",
    #     "-finder",
    #     action="store_true",
    #     help="Download a finding chart from Fritz.",
    # )

    cli_args = parser.parse_args()
    if not is_ztf_name(cli_args.name):
        logger.warn(f"Please provide a ZTF name. You entered {cli_args.name}")

    obs = Observability(ztf_id=cli_args.name)
    obs.plot_standards()
    # obs.plot_standards()
    # if cli_args.finding:
    # get_finding_chart(ztf_id=cli_args.name)
