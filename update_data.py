#!/usr/bin/env python3
import io
import os

import pandas as pd
import requests

DATA_URL = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv"

file_path = os.path.realpath(__file__)
file_dir = os.path.split(file_path)[0]
output_filepath = os.path.join(
    file_dir, "data/COVID-19_aantallen_gemeente_cumulatief.csv"
)


def update():
    req = requests.get(DATA_URL)
    if req.status_code != 200:
        print(f"Failed to request {DATA_URL}, HTTP status code {req.status_code}")
        return

    df = pd.read_csv(
        io.StringIO(req.text),
        sep=";",
    )
    print(f"Successful request to {DATA_URL}")
    temp_file = output_filepath + ".tmp"
    df.to_csv(
        temp_file,
        sep=";",
        index=False,
    )
    os.replace(temp_file, output_filepath)
    print("Success. File written!")


if __name__ == "__main__":
    print("Downloading file...")
    update()
