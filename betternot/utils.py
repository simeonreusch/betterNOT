#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import re


def is_ztf_name(name: str) -> bool:
    """
    Checks if a string adheres to the ZTF naming scheme
    """
    return re.match(r"^ZTF[1-2]\d[a-z]{7}$", name)
