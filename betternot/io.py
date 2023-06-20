#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

from pathlib import Path

basedir = Path(__file__).parents[1]


def get_object_dir(ztf_id: str) -> Path:
    directory = basedir / ztf_id
    directory.mkdir(parents=True, exist_ok=True)

    return directory
