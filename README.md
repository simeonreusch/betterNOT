# betterNOT
Toolset for preparing observations with the Nordic Optical Telescope (NOT). Currently only set up to work with ZTF transients. You need [Fritz](https://fritz.science) credentials.

The observability code is largely based on the [`NOT Observing Tools`](https://github.com/steveschulze/NOT_Observing_Tools) by S. Schulze.

Note the [observation guidelines](https://notes.simeonreusch.com/s/dHt_0XzwQ#)

## Installation
Clone the repository, `cd` into it and issue `poetry install`

## Usage
The package can be run with a command line interface. Simply issue
```
not ZTF23changeit ZTF23thistoo ...
```
This will generate a standard star observability plot, create obs plots for all ZTF objects, download the finding charts for them from Fritz and print the coordinates as well as the last observed magnitude.

Optionally, you can specify a desired date with `-date YYYY-MM-DD` (the default is today).

### Uploading spectra to WISeREP
You will need a [TNS](https://www.wis-tns.org) and [WISeREP](https://www.wiserep.org) bot token for this. Uploading spectra can be done as follows:
```python
from betternot.wiserep import Wiserep

Wiserep(
    ztf_id="ZTF23aaawbsc",
    spec_path="ZTF23aaawbsc_combined_3850.ascii",
    sandbox=True,
)
```
This will check TNS if an IAU object exists at the ZTF transient location, open the spectrum, extract the metadata, and upload the file to WISeREP as well as a report containing the extracted metadata.

After checking with the [WISeREP sandbox](https://sandbox.wiserep.org) that everything works fine, use `sandbox=False`