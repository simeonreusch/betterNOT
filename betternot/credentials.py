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

try:
    keyring.get_password("dummy", f"dummyfi_user")
    # get_credentials("dummy", f"dummyfi_user")
    keyring_available = True
except keyring.errors.NoKeyringError:
    keyring_available = False

keyring_available = False


def get_credentials(service, token=False):
    credentials = {}
    if keyring_available is True:
        if token is False:
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
            credentials.update({"user": username, "password": password})

        if token is True:
            token = keyring.get_password(service, f"{service}_token")
            if token is None:
                token = getpass.getpass(
                    prompt=f"Enter your {service} token: ", stream=None
                )
                keyring.set_password(service, f"{service}_token", token)
                logger.info(f"Got {service} credentials")
            credentials.update({"token": token})

    if keyring_available is False:
        if token is False:
            username = os.environ.get(f"{service}_user")
            password = os.environ.get(f"{service}_password")

            if username is None:
                username, password = io._load_id_(service)
            credentials.update({"user": username, "password": password})

        if token is True:
            token = os.environ.get(f"{service}_token")

            if token is None:
                logger.info(
                    f"This is a workaround using base64 obfuscation. If it asks for input: Enter an arbitrary username and the {service} token."
                )
                _, token = io._load_id_(service)
            credentials.update({"token": token})

    print(service)
    print(credentials)
    print("\n\n\n")

    return credentials
