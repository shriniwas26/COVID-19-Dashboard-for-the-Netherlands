#!/usr/bin/env python3
import requests
import os
import io
import pandas as pd

DATA_URL = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv"

file_path = os.path.realpath(__file__)
file_dir = os.path.split(file_path)[0]
output_filepath = os.path.join(
    file_dir,
    "data/COVID-19_aantallen_gemeente_cumulatief.csv"
)

def update():
    req = requests.get(DATA_URL)
    assert req.status_code == 200

    df = pd.read_csv(io.StringIO(req.text), sep=";")

    df.to_csv(
        output_filepath,
        sep=";",
        index=False,
        line_terminator="\r\n"
    )


if __name__ == "__main__":
    print("Downloading file...")
    update()
    print("Success. File written!")
