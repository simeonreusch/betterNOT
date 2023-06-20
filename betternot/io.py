#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

from pathlib import Path

import yaml  # type: ignore

basedir = Path(__file__).parents[1]


def get_object_dir(ztf_id: str) -> Path:
    directory = basedir / ztf_id
    directory.mkdir(parents=True, exist_ok=True)

    return directory


def get_date_dir(date: str) -> Path:
    directory = basedir / date
    directory.mkdir(parents=True, exist_ok=True)

    return directory


def load_config() -> dict:
    """
    Load the config (contains e.g. standard stars)
    """
    current_dir = Path(__file__)
    config_dir = current_dir.parents[1]
    config_file = config_dir / "config.yaml"

    with open(config_file, "r") as stream:
        config = yaml.safe_load(stream)

    return config
