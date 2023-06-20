# betterNOT
Toolset for preparing observations with the Nordic Optical Telescope (NOT). Currently only set up to work with ZTF transients. You need [Fritz](https://fritz.science) credentials.

The observability code is largely based on the [`NOT Observing Tools`](https://github.com/steveschulze/NOT_Observing_Tools) by S. Schulze.

Note the [observation guidelines](https://notes.simeonreusch.com/s/dHt_0XzwQ#)

## Installation
Clone the repository, `cd` into it and issue `poetry install`

## Usage
The package can be run with a command line interface. Simply issue
```
not [ZTF_ID]
```
followed by a set of options. Currently working:
```
not [ZTF_ID] -finding
```
will download a finding chart for the ZTF object in question.