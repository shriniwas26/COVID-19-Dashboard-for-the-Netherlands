#! /usr/bin/env python3

import datetime
import os
import sys

import dash
import dash.dcc as dcc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import html
from dash.dependencies import Input, Output

import update_data

##### Define constants #####
PER_POPULATION = 100
COVID_DATA_FILE = "data/COVID-19_aantallen_gemeente_cumulatief.csv"
DEFAULT_MUNICIPALITIES = ["Amsterdam", "Eindhoven", "Heerlen", "Nijmegen"]

##### Utility functions #####
def round_significant_digits(x, n=2):
    if type(x) in [int, float]:
        if x == 0:
            return 0
        if x > 1:
            return round(x, n)

    power = 10 ** np.ceil(np.log10(abs(x)))
    return round(x / power, n) * power


## Metrics to display ##
METRICS = ["Total_reported", "Hospital_admission", "Deceased"]

COVID_DATA = pd.read_csv(COVID_DATA_FILE, sep=";")
COVID_DATA["Date_of_report"] = pd.to_datetime(COVID_DATA["Date_of_report"])

datetime_last_updated = datetime.datetime.fromtimestamp(
    os.path.getmtime(COVID_DATA_FILE)
)
datetime_now = datetime.datetime.now()
print(
    f"Date now: {datetime_now.strftime('%Y-%m-%d %H:%M:%S')}. "
    f"Last updated: {datetime_last_updated.strftime('%Y-%m-%d %H:%M:%S')}"
)
if (datetime_now - datetime_last_updated) >= datetime.timedelta(days=1):
    print("Data fetched before 1 day, fetching from URL")
    try:
        update_data.update()
        COVID_DATA = pd.read_csv(COVID_DATA_FILE, sep=";")
        COVID_DATA["Date_of_report"] = pd.to_datetime(COVID_DATA["Date_of_report"])
    except:
        print("Cannot read url reverting to local, reading locally.")


# Remove all data points which don't have a municipality name
COVID_DATA = COVID_DATA[COVID_DATA["Municipality_name"] != ""]
COVID_DATA = COVID_DATA[(COVID_DATA["Municipality_name"].notna())]

## Replace faulty data ##
COVID_DATA["Province"] = COVID_DATA["Province"].replace(
    {
        "FryslÃ¢n": "Friesland",
        "Fryslân": "Friesland",
    }
)

## Disambiguate Municipality name by Municipality code ##
COVID_DATA["Municipality_name"] = COVID_DATA.groupby("Municipality_code")[
    "Municipality_name"
].transform(lambda x: sorted(x)[0])

##  Read population data ##
mun_population_data = pd.read_csv("data/NL_Population_Latest.csv")
mun_population_data = mun_population_data.rename(
    columns={"PopulationOn31December_20": "Population"}
)

## Merge the population data ##
COVID_DATA = COVID_DATA.merge(
    mun_population_data, left_on="Municipality_code", right_on="Regions", how="inner"
)

## Compute daily values ##
COVID_DATA = COVID_DATA.sort_values(
    by=["Municipality_code", "Municipality_name", "Date_of_report"]
)
for metric in METRICS:
    COVID_DATA[f"{metric}_daily"] = COVID_DATA.groupby("Municipality_name")[
        metric
    ].transform(lambda x: x.diff().fillna(0))


for covid_metric in METRICS:
    COVID_DATA[f"{covid_metric}_daily_population_adjusted"] = (
        COVID_DATA[f"{covid_metric}_daily"] / COVID_DATA["Population"] * PER_POPULATION
    )
    COVID_DATA[f"{covid_metric}_population_adjusted"] = (
        COVID_DATA[covid_metric] / COVID_DATA["Population"] * PER_POPULATION
    )


def get_provincial_data():
    df = pd.read_csv(COVID_DATA_FILE, sep=";")
    df = df[
        df["Municipality_code"].isna() & df["Municipality_name"].isna()
    ].reset_index(drop=True)
    df = df.sort_values(by=["Date_of_report", "Province"])
    for metric in METRICS:
        df[f"{metric}_daily"] = COVID_DATA.groupby("Province")[metric].transform(
            lambda x: x.diff().fillna(0)
        )
    return df


PROVINCIAL_COVID_DATA = get_provincial_data()

PROVINCIAL_POPULATION_DATA = pd.read_csv("data/Netherlands_population.csv").rename(
    columns={"Population Estimate 2020-01-01": "Population"}
)
PROVINCIAL_POPULATION_DATA = PROVINCIAL_POPULATION_DATA[
    PROVINCIAL_POPULATION_DATA["Status"] == "Province"
].reset_index()
PROVINCIAL_POPULATION_DATA["Short Name"] = PROVINCIAL_POPULATION_DATA["Name"].apply(
    lambda x: x.split()[0]
)


PROVINCIAL_COVID_DATA = PROVINCIAL_COVID_DATA.merge(
    PROVINCIAL_POPULATION_DATA, how="inner", left_on="Province", right_on="Short Name"
)

for covid_metric in METRICS:
    PROVINCIAL_COVID_DATA[f"{covid_metric}_daily_population_adjusted"] = (
        PROVINCIAL_COVID_DATA[f"{covid_metric}_daily"]
        / PROVINCIAL_COVID_DATA["Population"]
        * PER_POPULATION
    )
    PROVINCIAL_COVID_DATA[f"{covid_metric}_population_adjusted"] = (
        PROVINCIAL_COVID_DATA[covid_metric]
        / PROVINCIAL_COVID_DATA["Population"]
        * PER_POPULATION
    )

## Calculate unique municipalities which have both population and covid data ##
UNIQUE_MUNICIPALITIES = np.unique(COVID_DATA["Municipality_name"])
UNIQUE_PROVINCES = np.unique(PROVINCIAL_COVID_DATA["Province"])

## Setup the dash app ##
app = dash.Dash(
    __name__,
    assets_folder="assets",
    url_base_pathname="/",
    show_undo_redo=True,
)
app.title = "COVID-19 Dashboard - The Netherlands"
server = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                html.H6("Select municipalities:"),
                dcc.Dropdown(
                    id="selected_municipalities",
                    options=[
                        {"label": i, "value": i} for i in sorted(UNIQUE_MUNICIPALITIES)
                    ],
                    value=DEFAULT_MUNICIPALITIES,
                    style={
                        "textAlign": "center",
                        "align": "center",
                        "border-radius": "25px",
                        "margin-left": "5%",
                        "width": "90%",
                    },
                    multi=True,
                ),
                html.Br(),
            ],
            style={
                "width": "35%",
                "display": "inline-block",
                "vertical-align": "top",
                "textAlign": "center",
                "border": "2px black solid",
                "border-radius": "25px",
                "margin": "5px",
                "height": "100%",
            },
        ),
        html.Div(
            [
                html.H6("Metric:"),
                dcc.Dropdown(
                    id="covid_metrics",
                    options=[
                        {"label": i.replace("_", " ").title(), "value": i}
                        for i in METRICS
                    ],
                    value=["Total_reported", "Deceased"],
                    multi=True,
                    style={
                        "textAlign": "left",
                        "align": "center",
                        "border-radius": "25px",
                        "margin-left": "1%",
                        "width": "98%",
                    },
                ),
                html.Br(),
            ],
            style={
                "width": "20%",
                "display": "inline-block",
                "vertical-align": "top",
                "textAlign": "center",
                "border": "2px black solid",
                "border-radius": "25px",
                "margin": "5px",
                "height": "100%",
            },
        ),
        html.Div(
            [
                html.H6("Data type:"),
                dcc.RadioItems(
                    id="data_type",
                    options=[
                        {"label": i, "value": i}
                        for i in ["Absolute", "Population Adjusted"]
                    ],
                    value="Population Adjusted",
                    style={
                        "textAlign": "left",
                        "align": "center",
                        "border-radius": "25px",
                        "margin-left": "5%",
                        "width": "90%",
                    },
                ),
                html.Br(),
            ],
            style={
                "width": "12%",
                "display": "inline-block",
                "vertical-align": "top",
                "textAlign": "center",
                "border": "2px black solid",
                "border-radius": "25px",
                "margin": "5px",
                "height": "100%",
            },
        ),
        html.Div(
            [
                html.H6("Series type"),
                dcc.RadioItems(
                    id="series_type",
                    options=[{"label": i, "value": i} for i in ["Cumulative", "Daily"]],
                    value="Daily",
                    style={
                        "textAlign": "left",
                        "align": "center",
                        "border-radius": "25px",
                        "margin-left": "5%",
                        "width": "90%",
                    },
                ),
                html.Br(),
            ],
            style={
                "width": "12%",
                "display": "inline-block",
                "vertical-align": "top",
                "textAlign": "center",
                "border": "2px black solid",
                "border-radius": "25px",
                "margin": "5px",
                "height": "100%",
            },
        ),
        html.Div(
            [
                html.H6("Moving average"),
                dcc.Input(
                    id="moving_avg",
                    type="number",
                    placeholder="Rolling Window",
                    min=1,
                    max=100,
                    step=1,
                    value=5,
                    debounce=False,
                    style={
                        "align": "center",
                        "vertical-align": "top",
                        "textAlign": "left",
                        "border-radius": "25px",
                        "margin-left": "30%",
                        "margin-right": "30%",
                        "width": "40%",
                    },
                ),
                html.Br(),
                html.Br(),
            ],
            style={
                "width": "10%",
                "display": "inline-block",
                "vertical-align": "top",
                "textAlign": "center",
                "border": "2px black solid",
                "border-radius": "25px",
                "margin": "5px",
                "height": "100%",
            },
        ),
        html.Hr(),
        html.Div(
            [],
            style={"width": "99vw", "display": "inline-block", "padding": "0 20"},
            id="mun_figure",
        ),
        html.Hr(),
        html.Br(),
        html.Div(
            [
                html.H6("Select provinces:"),
                dcc.Dropdown(
                    id="selected_provinces",
                    options=[{"label": i, "value": i} for i in UNIQUE_PROVINCES],
                    value=sorted(
                        ["Zuid-Holland", "Noord-Brabant", "Utrecht", "Limburg"]
                    ),
                    style={
                        "textAlign": "center",
                        "align": "center",
                        "border-radius": "25px",
                        "margin-left": "5%",
                        "width": "90%",
                    },
                    multi=True,
                ),
                html.Br(),
            ],
            style={
                "width": "40%",
                "display": "inline-block",
                "vertical-align": "top",
                "textAlign": "center",
                "border": "2px black solid",
                "border-radius": "25px",
                "margin": "5px",
            },
        ),
        html.Br(),
        html.Div(
            [],
            style={"width": "99vw", "display": "inline-block", "padding": "0 20"},
            id="prov_figure",
        ),
    ]
)


@app.callback(
    Output("mun_figure", "children"),
    Input("selected_municipalities", "value"),
    Input("covid_metrics", "value"),
    Input("moving_avg", "value"),
    Input("data_type", "value"),
    Input("series_type", "value"),
)
def process_and_render_municipalities(
    selected_municipalities, covid_metrics, moving_avg, data_type, series_type
):
    selected_municipalities = np.unique(selected_municipalities)
    if len(selected_municipalities) > 0:
        mun_data = COVID_DATA[
            COVID_DATA["Municipality_name"].isin(selected_municipalities)
        ].copy()
    else:
        return go.Figure()

    figures = []
    for covid_metric in covid_metrics:
        column_name = covid_metric
        if series_type == "Daily":
            column_name = f"{covid_metric}_daily"
        if data_type == "Population Adjusted":
            column_name = f"{column_name}_population_adjusted"

        if moving_avg not in [None, 0, 1]:
            mun_data[column_name] = mun_data.groupby("Municipality_name")[
                column_name
            ].transform(
                lambda x: x[::-1]
                .rolling(window=int(moving_avg), min_periods=1, center=False)
                .mean()[::-1]
            )

        ## Add figure ##
        daily_mun_figure = go.Figure()
        for grp, df in mun_data.groupby("Municipality_name"):
            daily_mun_figure.add_trace(
                go.Scatter(
                    x=df["Date_of_report"],
                    y=df[column_name],
                    name=grp,
                    mode="markers+lines",
                    line_shape="spline",
                    marker={"size": 2},
                    hovertemplate="%{x}<br>%{y}",
                )
            )
        daily_mun_figure.update_layout(
            title=f"{column_name}".title()
            .replace("_", " ")
            .replace("Population Adjusted", f"per {PER_POPULATION} people"),
            title_x=0.5,
        )
        daily_mun_figure.update_xaxes(title="Date of report")

        figures.append(daily_mun_figure)

    children = [
        dcc.Graph(
            figure=fig,
            style={
                "width": "{}vw".format(int(99 / len(covid_metrics)) - 1),
                "display": "inline-block",
                "margin": "5px",
                "height": "100%",
            },
        )
        for fig in figures
    ]

    return children


@app.callback(
    Output("prov_figure", "children"),
    Input("selected_provinces", "value"),
    Input("covid_metrics", "value"),
    Input("moving_avg", "value"),
    Input("data_type", "value"),
    Input("series_type", "value"),
)
def process_and_render_provinces(
    selected_provinces, covid_metrics, moving_avg, data_type, series_type
):
    if len(selected_provinces) > 0:
        province_data_selected = PROVINCIAL_COVID_DATA[
            PROVINCIAL_COVID_DATA["Province"].isin(selected_provinces)
        ].copy()
    else:
        province_data_selected = PROVINCIAL_COVID_DATA.copy()

    figures = []
    for covid_metric in covid_metrics:
        column_name = covid_metric
        if series_type == "Daily":
            column_name = f"{column_name}_daily"
        if data_type == "Population Adjusted":
            column_name = f"{column_name}_population_adjusted"

        if moving_avg not in [None, 0, 1]:
            province_data_selected[
                f"{covid_metric}_daily"
            ] = province_data_selected.groupby("Province")[
                f"{covid_metric}_daily"
            ].transform(
                lambda x: x[::-1]
                .rolling(window=int(moving_avg), min_periods=1, center=False)
                .mean()[::-1]
            )

        ## Round the data to 3 significant digits ##
        province_data_selected[column_name] = province_data_selected[column_name].apply(
            lambda x: round_significant_digits(x, 3)
        )
        province_data_selected[covid_metric] = province_data_selected[
            covid_metric
        ].apply(lambda x: round_significant_digits(x, 3))

        province_fig = go.Figure()
        for grp, df in province_data_selected.groupby("Province"):
            province_fig.add_trace(
                go.Scatter(
                    x=df["Date_of_report"],
                    y=df[column_name],
                    name=grp,
                    mode="markers+lines",
                    line_shape="spline",
                    marker={"size": 2},
                    hovertemplate="%{x}<br>%{y}",
                )
            )
        province_fig.update_layout(
            title=f"{column_name}".title()
            .replace("_", " ")
            .replace("Population Adjusted", f"per {PER_POPULATION} people"),
            title_x=0.5,
        )
        province_fig.update_xaxes(title="Date of report")

        figures.append(province_fig)

    children = [
        dcc.Graph(
            figure=fig,
            style={
                "width": "{}vw".format(int(99 / len(covid_metrics)) - 1),
                "display": "inline-block",
                "margin": "5px",
                "height": "100%",
            },
        )
        for fig in figures
    ]

    return children


def main():
    APP_PORT = 8080
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Starting dashboard for COVID-19 data in The Netherlands at {time_now}")
    app.run_server(debug=True, host="0.0.0.0", port=APP_PORT)


if __name__ == "__main__":
    sys.exit(main())
