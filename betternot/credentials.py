#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause

import getpass
import logging
import os
import warnings
from os import environ

import keyring
from ztfquery import io  # type: ignore

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HEADLESS = False


if environ.get("BETTERNOT_MODE") == "HEADLESS":
    HEADLESS = True


def get_user_and_password(service: str):
    """
    Default: Try the systemwide keychain - fully encrypted
    (works at least on Debian, Ubuntu and Mac)
    """
    if not HEADLESS:
        try:
            username = keyring.get_password(service, f"{service}_user")
            password = keyring.get_password(service, f"{service}_password")

            if username is None:
                username = input(f"Enter your {service} login: ")
                password = getpass.getpass(
                    prompt=f"Enter your {service} password: ", stream=None
                )
                keyring.set_password(service, f"{service}_user", username)
                keyring.set_password(service, f"{service}_password", password)

            logger.info(f"Got {service} credentials")

            return username, password

        # Some systems don't provide the luxury of a system-wide keychain
        # Use workaround with base64 obfuscation
        except keyring.errors.NoKeyringError:
            username, password = io._load_id_(service)
            return username, password
    else:
        username, password = io._load_id_(service)
        return username, password


def get_user(service: str):
    """ """
    if not HEADLESS:
        try:
            username = keyring.get_password(service, f"{service}_user")

            if username is None:
                username = input(f"Enter your {service} login: ")
                keyring.set_password(service, f"{service}_user", username)

        except keyring.errors.NoKeyringError:
            logger.info(
                f"This is a workaround using base64 obfuscation. If it asks for input: Enter the {service} username and an arbitrary password."
            )
            username, _ = io._load_id_(service)
    else:
        logger.info(
            f"This is a workaround using base64 obfuscation. If it asks for input: Enter the {service} username and an arbitrary password."
        )
        username, _ = io._load_id_(service)

    logger.info(f"Got {service} username")
    return username


def get_password(service: str):
    """ """
    if not HEADLESS:
        try:
            password = keyring.get_password(service, f"{service}_password")

            if password is None:
                password = getpass.getpass(
                    prompt=f"Enter your {service} password: ", stream=None
                )
                keyring.set_password(service, f"{service}_password", password)

        except keyring.errors.NoKeyringError:
            logger.info(
                f"This is a workaround using base64 obfuscation. If it asks for input: Enter an arbitrary username and the {service} password."
            )
            _, password = io._load_id_(service)

    else:
        logger.info(
            f"This is a workaround using base64 obfuscation. If it asks for input: Enter an arbitrary username and the {service} password."
        )
        _, password = io._load_id_(service)

    logger.info(f"Got {service} password")
    return password
