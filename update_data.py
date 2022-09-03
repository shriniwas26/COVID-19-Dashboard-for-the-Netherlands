#!/usr/bin/env python3
import requests
import os
import io
import pandas as pd

DATA_URL = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv"

self_file_path = os.path.realpath(__file__)
self_file_dir = os.path.split(self_file_path)[0]
output_filepath = os.path.join(
    self_file_dir,
    "data/COVID-19_aantallen_gemeente_cumulatief.csv"
)

def update():
    req = requests.get(DATA_URL)
    assert req.status_code == 200
    df = pd.read_csv(io.StringIO(req.text), sep=";")
    print(f"Successful request to {DATA_URL}")
    temp_file = output_filepath + ".tmp"
    df.to_csv(
        temp_file,
        sep=";",
        index=False,
        line_terminator="\r\n"
    )
    os.replace(temp_file, output_filepath)


if __name__ == "__main__":
    print("Downloading file...")
    update()
    print("Success. File written!")
