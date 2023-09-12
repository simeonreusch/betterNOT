import logging

from betternot.wiserep import Wiserep

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sandbox = False

Wiserep(
    ztf_id="ZTF23aaawbsc",
    spec_path="ZTF23aaawbsc_2023-09-11_3850.ascii",
    sandbox=sandbox,  # set False for actual upload
    quality="medium",  # "low", "medium" or "high". Default: "medium"
)

Wiserep(
    ztf_id="ZTF23aakmewi",
    spec_path="ZTF23aakmewi_2023-09-11_3850.ascii",
    sandbox=sandbox,  # set False for actual upload
    quality="high",  # "low", "medium" or "high". Default: "medium"
)
