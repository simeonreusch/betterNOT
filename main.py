#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import argparse
import datetime
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
    """
    This is invoked on the command line by `not`
    """
    parser = argparse.ArgumentParser(description="Various NOT tools")
    parser.add_argument(
        "names",
        type=str,
        nargs="+",
        help="Provide one or more ZTF names (e.g. ZTF19aaelulu)",
    )
    parser.add_argument(
        "-date",
        "-d",
        type=str,
        default=None,
        help="Here you can provide a date in the form YYYY-MM-DD. If none is given, the current day is chosen automatically.",
    )
    parser.add_argument(
        "-site",
        "-s",
        type=str,
        default="not",
        help="Here you can provide a desired observation site. Defaults to La Palma.",
    )

    cli_args = parser.parse_args()

    if cli_args.date is None:
        date = datetime.date.today().strftime("%Y-%m-%d")
    else:
        date = cli_args.date

    correct_ids = []

    for ztf_id in cli_args.names:
        if is_ztf_name(ztf_id):
            correct_ids.append(ztf_id)

    if len(correct_ids) < len(cli_args.names):
        malformed = [i for i in cli_args.names if i not in correct_ids]
        logger.warn(
            f"Please check that each name is a correct ZTF name. These are malformed and will be skipped now: {', '.join(malformed)}"
        )

    obs = Observability(ztf_ids=correct_ids, date=date, site=cli_args.site)
    # obs.plot_standards()
    # obs.plot_targets()
    # for ztf_id in correct_ids:
    #     get_finding_chart(ztf_id=ztf_id, date=date)
    obs.print_info()
