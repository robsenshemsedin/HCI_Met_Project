# HCI Met Project Dataset

## Overview

This repository contains the cleaned working dataset prepared for the Human-Computer Interaction and Information Visualization course project.

The dataset is based on The Metropolitan Museum of Art Open Access collection.

Official source:
https://github.com/metmuseum/openaccess

## Files

| File                     | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| `met_clean_30000.csv`    | Cleaned working dataset with 30,000 records and 35 variables. |
| `clean_met_dataset.py`   | Python script used to clean and filter the original dataset.  |
| `variable_dictionary.md` | Description of the variables included in the cleaned dataset. |

## Raw Dataset

The original dataset is `MetObjects.csv`, provided by The Metropolitan Museum of Art Open Access repository.

The raw dataset was not uploaded here because of its large file size. It can be downloaded from the official source:

https://github.com/metmuseum/openaccess

## Cleaning Summary

The original dataset used locally contained:

* 484,956 records
* 54 variables

After cleaning, a full cleaned dataset was generated locally with:

* 191,260 records
* 35 variables

For practical use in the project, a working dataset was created with:

* 30,000 records
* 35 variables

## Cleaning Steps

The Python script performs the following steps:

1. Selects variables useful for visualization and analysis.
2. Keeps public-domain objects.
3. Removes records with missing essential information.
4. Cleans date fields.
5. Creates `object_mid_year`.
6. Creates simplified `time_period_group`.
7. Creates simplified `medium_group`.
8. Creates `visibility_group`.
9. Exports the 30,000-record working dataset.

## Requirements

The cleaning script uses:

```bash
pip install pandas openpyxl numpy
```

## Running the Script

Place the original `MetObjects.xlsx` file in the same folder as the script, then run:

```bash
python clean_met_dataset.py
```

The script will generate:

```text
met_clean_full.csv
met_clean_30000.csv
```
