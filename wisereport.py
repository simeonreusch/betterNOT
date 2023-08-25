#!/usr/bin/env python3

import json
import logging
import os
import re
import sys
import time
from collections import OrderedDict
from pathlib import Path

import requests
import yaml

api_key_json_keyword = "bot_api_key"

# current working directory
cwd = os.getcwd()

# sleeping time (in sec)
TIME_SLEEP = 2

# max number of time to check response
LOOP_COUNTER = 60

# http errors
http_errors = {
    304: "Error 304: Not Modified: There was no new data to return.",
    400: "Error 400: Bad Request: The request was invalid. "
    "An accompanying error message will explain why.",
    403: "Error 403: Forbidden: The request is understood, but it has "
    "been refused. An accompanying error message will explain why.",
    404: "Error 404: Not Found: The URI requested is invalid or the "
    "resource requested, such as a category, does not exists.",
    500: "Error 500: Internal Server Error: Something is broken.",
    503: "Error 503: Service Unavailable.",
}

old_stdout = sys.stdout


def is_tns_name(name: str) -> bool:
    """
    Checks if a string adheres to the TNS naming scheme
    """
    if re.match(r"^AT|SN(19|20)\d\d[a-z]{3,4}$", name):
        matches = True
    else:
        matches = False
    return matches


# function for uploading files trough api
def upload_files(url, list_of_files):
    try:
        # url for uploading files
        upload_url = url + "/file-upload"
        # headers
        headers = {
            "User-Agent": 'tns_marker{"tns_id":' + str(BOT_ID) + ', "type":"bot",'
            ' "name":"' + BOT_NAME + '"}'
        }
        # api key data
        api_data = {api_key_json_keyword: api_key}
        # construct a dictionary of files and their data
        files_data = {}
        for i in range(len(list_of_files)):
            file_name = list_of_files[i]
            file_path = os.path.join(files_folder, file_name)
            key = "files[" + str(i) + "]"
            if file_name.lower().endswith((".asci", ".ascii")):
                value = (file_name, open(file_path), "text/plain")
            else:
                value = (file_name, open(file_path, "rb"), "application/fits")
            files_data[key] = value
        # upload all files using request module
        response = requests.post(
            upload_url, headers=headers, data=api_data, files=files_data
        )

        return response
    except Exception as e:
        return [None, "Error message : \n" + str(e)]


def search_tns():
    """
    Query the TNS API for a given location
    """
    # if not is_tns_name(name):
    # raise ValueError("String is not a TNS name")

    tns_api_token = "d1971f402dc6d10eaa214708db1d5db2bbd06aaa"

    tns_bot_id = "115364"
    tns_bot_name = "ZTF_DESY"

    queryurl_tns = "https://www.wis-tns.org/api/get/object"

    tns_marker = (
        'tns_marker{"tns_id": "'
        + str(tns_bot_id)
        + '", "type": "bot", "name": "'
        + tns_bot_name
        + '"}'
    )
    headers = {"User-Agent": tns_marker}

    get_obj = {
        "ra": "05:24:18.0",
        "dec": "+09:10:37.0",
        "radius": "300",
        "units": "arcsec",
        # "objname": "",
        # "objname_exact_match": 0,
        # "internal_name": "Gaia16azh",
        "internal_name_exact_match ": 0,
        "objid": "",
        "public_timestamp": "",
    }

    json_file = json.dumps(get_obj)

    get_data = {"api_key": tns_api_token, "data": json_file}

    response = requests.post(queryurl_tns, headers=headers, data=get_data)

    logger.info(response.json())
    quit()


# function that checks response and
# returns True if everything went OK
# or returns False if something went wrong
def check_response(response):
    # if response exists
    if None not in response:
        # take status code of that response
        status_code = int(response.status_code)
        if status_code == 200:
            # response as json data
            json_data = response.json()
            # id code
            id_code = str(json_data["id_code"])
            # id message
            id_message = str(json_data["id_message"])
            # print id code and id message
            logger.info("ID code = " + id_code)
            logger.info("ID message = " + id_message)

            if id_code == "200" and id_message == "OK":
                return True

            elif id_code == "400" and id_message == "Bad request":
                return None
            else:
                return False
        else:
            # if status code is not 200, check if it exists in
            # http errors
            if status_code in list(http_errors.keys()):
                logger.info(
                    list(http_errors.values())[
                        list(http_errors.keys()).index(status_code)
                    ]
                )
            else:
                logger.info("Undocumented error.")
            return False
    else:
        # response doesn't exists, print error
        logger.info(response[1])
        return False


# uploading files and printing reply
def upload(url, list_of_files):
    # upload files and checking response
    logger.info(f"Uploading the following files on the WISeREP:\n")
    for f in list_of_files:
        logger.info(f)
    time.sleep(TIME_SLEEP)
    response = upload_files(url, list_of_files)
    response_check = check_response(response)
    time.sleep(TIME_SLEEP)
    # if files are uploaded
    if response_check == True:
        logger.info("\nThe following files were uploaded on the WISeREP : \n")
        time.sleep(TIME_SLEEP)
        # response as json data
        json_data = response.json()
        # list of uploaded files
        uploaded_files = json_data["data"]
        for i in range(len(uploaded_files)):
            logger.info(f"filename: {str(uploaded_files[i])}")

        time.sleep(TIME_SLEEP)
        return uploaded_files
    else:
        logger.info("\nFiles were not uploaded to the WISeREP.\n")
        time.sleep(TIME_SLEEP)
        return False


# function for changing data to json format
def format_to_json(source):
    # change data to json format and return
    parsed = json.loads(source, object_pairs_hook=OrderedDict)
    result = json.dumps(parsed, indent=4)
    return result


# function for sending json metadata
def send_json_report(url, json_report):
    try:
        # url for sending json metadata
        json_url = url + "/bulk-report"
        # headers
        headers = {
            "User-Agent": 'tns_marker{"tns_id":' + str(BOT_ID) + ', "type":"bot",'
            ' "name":"' + BOT_NAME + '"}'
        }

        json_read = format_to_json(open(json_report).read())

        json_payload = {api_key_json_keyword: api_key, "data": json_read}

        response = requests.post(json_url, headers=headers, data=json_payload)

        return response

    except Exception as e:
        return [None, "Error message : \n" + str(e)]


# Disable print
def blockPrint():
    sys.stdout = open(os.devnull, "w")


# Restore print
def enablePrint():
    sys.stdout.close()
    sys.stdout = old_stdout


# function for getting reply from report
def reply(url, report_id):
    try:
        # url for getting report reply
        reply_url = url + "/bulk-report-reply"
        # headers
        headers = {
            "User-Agent": 'tns_marker{"tns_id":' + str(BOT_ID) + ', "type":"bot",'
            ' "name":"' + BOT_NAME + '"}'
        }
        # construct a dictionary of api key data and report id
        reply_data = {api_key_json_keyword: api_key, "report_id": report_id}
        # send report ID using request module
        response = requests.post(reply_url, headers=headers, data=reply_data)
        # return response
        return response
    except Exception as e:
        return [None, "Error message : \n" + str(e)]


# sending report id to get reply of the report
# and printing that reply


def print_reply(url, report_id):
    # sending reply using report id and checking response
    logger.info("Retrieving reply for the report ID " + report_id + " ...\n")
    time.sleep(TIME_SLEEP)
    reply_res = reply(url, report_id)
    reply_res_check = check_response(reply_res)
    time.sleep(TIME_SLEEP)
    # if reply is sent
    if reply_res_check == True:
        logger.info("\nThe report was successfully processed on the WISeREP.\n")
        time.sleep(TIME_SLEEP)
        # reply response as json data
        json_data = reply_res.json()
        # print feedback of the response
        logger.info('"feedback":')
        logger.info(f"{json.dumps(json_data['data']['feedback'], indent=4)}\n")

        time.sleep(TIME_SLEEP)
        return True
    else:
        if reply_res_check != None:
            logger.info("\nThe report doesn't exist on the WISeREP.\n")
            time.sleep(TIME_SLEEP)
        else:
            logger.info(
                "\nThe report was not processed on the WISeREP "
                "because of the bad request(s).\n"
            )
            # reply response as json data
            json_data = reply_res.json()
            logger.info('"feedback":')
            logger.info(f"{json.dumps(json_data['data']['feedback'], indent=4)}\n")

            time.sleep(TIME_SLEEP)
        return False


# sending tsv or json metadata file and printing reply
def send_metadata(url, metadata):
    # sending metadata and checking response
    logger.info(f"Sending {str(metadata)} to the WISeREP...\n")
    time.sleep(TIME_SLEEP)
    # choose which function to call
    response = send_json_report(url, metadata)
    response_check = check_response(response)
    time.sleep(TIME_SLEEP)
    # if metadata is sent
    if response_check == True:
        logger.info("\nThe metadata was sent to the WISeREP.\n")
        time.sleep(TIME_SLEEP)
        # report response as json data
        json_data = response.json()
        # taking report id
        report_id = str(json_data["data"]["report_id"])
        logger.info("Report ID = " + report_id + "\n")
        time.sleep(TIME_SLEEP)
        # sending report id to get reply of the report
        # and printing that reply
        # waiting for report to arrive before sending reply
        # for report id
        # blockPrint()
        counter = 0
        while True:
            time.sleep(TIME_SLEEP - 1)
            reply_response = reply(url, report_id)
            reply_res_check = check_response(reply_response)
            if reply_res_check != False or counter >= LOOP_COUNTER:
                break
            counter += 1
        # enablePrint()
        print_reply_response = print_reply(url, report_id)
        return print_reply_response
    else:
        logger.warn("\nThe metadata was not sent to the WISeREP.\n")
        time.sleep(TIME_SLEEP)
        return False


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# search_tns()
# quit()
# WISeREP server
# WISeREP="www.wiserep.org"
WISeREP = "sandbox.wiserep.org"

# url of WISeREP API
URL_WIS_API = "https://" + WISeREP + "/api"

# ID of your Bot:
BOT_ID = 1234

# name of your Bot:
BOT_NAME = "OKC_ZTF"

# API key of your Bot:
api_key = os.environ.get("WISEREP_TOKEN")

# folder for files
files_folder = os.path.join(cwd, "files_for_uploading")

# files for upload
FILES = ["example.ascii"]

# uploading files
upload_res = upload(URL_WIS_API, FILES)

# sending JSON metadata
if upload_res != False:
    spec_server_name = upload_res[0]
    with open("template.yaml", "r") as stream:
        try:
            metadata = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.warn(exc)

    metadata["objects"][0]["spectra"]["spectra_group"][0][
        "ascii_file"
    ] = spec_server_name

    json_report = Path("out.json")
    with open(json_report, "w") as f:
        json.dump(metadata, f)

    metadata_reply = send_metadata(URL_WIS_API, json_report)
    if metadata_reply == False:
        logger.info("Resolve that and run program again.\n")
        time.sleep(TIME_SLEEP)
        # exit the program
        sys.exit()
