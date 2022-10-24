#!/usr/bin/env python3
import json
import os
import datetime

import pandas as pd

DATA_URL = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv"
SELF_FILE_PATH = os.path.realpath(__file__)
SELF_FILE_DIR = os.path.split(SELF_FILE_PATH)[0]


def update():
    output_filepath = os.path.join(
        SELF_FILE_DIR, "data", "COVID-19_aantallen_gemeente_cumulatief.csv"
    )
    df = pd.read_csv(DATA_URL, sep=";")
    print(f"Successful request to {DATA_URL}")
    df.to_csv(output_filepath, sep=";", index=False, lineterminator="\n")

if __name__ == "__main__":
    print("Downloading file...")
    update()
    print("Success. File written!")
