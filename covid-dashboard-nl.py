import datetime
import json
import sys
import time

import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.figure_factory as ff
import scipy
import waitress
from dash.dependencies import Input, Output


app = dash.Dash(__name__)
app.title = "COVID-19 Dashboard - The Netherlands"

DATA_FILENAME = "COVID-19_aantallen_gemeente_cumulatief.csv"

initial_read = pd.read_csv(DATA_FILENAME, sep=';')
initial_read = initial_read[initial_read["Municipality_name"] != ""]
initial_read = initial_read[initial_read["Municipality_name"].notna()]

unique_municipalities = sorted(initial_read["Municipality_name"].unique())
unique_provinces = sorted(initial_read["Province"].unique())


app.layout = html.Div([
    html.Div([
        html.H6("Select municipalities:"),
        dcc.Dropdown(
            id='selected_municipalities',
            options=[{'label': i, 'value': i} for i in unique_municipalities],
            value=sorted(["'s-Gravenhage", 'Utrecht', 'Eindhoven', 'Heerlen']),
            style={
                'textAlign': 'center',
                'align': 'center',
                'border-radius': '25px',
                'margin-left': '5%',
                'width': '90%'
            },
            multi=True,
        ),
        html.Br(),
    ], style={
        'width': '35%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px'
    }),
    html.Div([
        html.H6("Moving Average"),
        dcc.Input(
            id="moving_avg",
            type="number",
            placeholder="Rolling Window",
            min=1,
            max=50,
            step=1,
            value=5,
            debounce=False,
            style={
                'align': 'center',
                'border-radius': '25px',
                'margin': '1px',
                'width': '70%'}
        ),
        html.Br(),
        html.Br()
    ], style={
        'width': '8%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px'
    }),
    html.Br(),
    html.Div([
        dcc.Graph(
            id='daily_figure',
        )
    ], style={
        'width': '49%',
        'display': 'inline-block',
        'padding': '0 20'
    }),
    html.Div([
        dcc.Graph(
            id='total_figure',
        )
    ], style={
        'width': '49%',
        'display': 'inline-block',
        'padding': '0 20'
    }),
    html.Hr(),
    html.Br(),
    html.Div([
        html.H6("Select provinces:"),
        dcc.Dropdown(
            id='selected_provinces',
            options=[{'label': i, 'value': i} for i in unique_provinces],
            value=sorted(['Zuid-Holland', 'Noord-Brabant', 'Utrecht', 'Limburg']),
            style={
                'textAlign': 'center',
                'align': 'center',
                'border-radius': '25px',
                'margin-left': '5%',
                'width': '90%'
            },
            multi=True,
        ),
        html.Br(),
    ], style={
        'width': '35%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px'
    }),
    html.Div([
        html.H6("Moving Average"),
        dcc.Input(
            id="moving_avg_province",
            type="number",
            placeholder="Rolling Window",
            min=1,
            max=50,
            step=1,
            value=5,
            debounce=False,
            style={
                'align': 'center',
                'border-radius': '25px',
                'margin': '1px',
                'width': '70%'}
        ),
        html.Br(),
        html.Br()
    ], style={
        'width': '8%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px'
    }),
    html.Br(),
    html.Div([
        dcc.Graph(
            id='daily_province_figure',
        )
    ], style={
        'width': '49%',
        'display': 'inline-block',
        'padding': '0 20'
    }),

])


@app.callback(
    Output('daily_figure', 'figure'),
    Output('total_figure', 'figure'),
    Input('selected_municipalities', 'value'),
    Input('moving_avg', 'value'),
)
def generate_data(selected_municipalities, moving_avg):
    data = pd.read_csv(DATA_FILENAME, sep=';')
    data = data[data["Municipality_name"] != ""]
    data = data[data["Municipality_name"].notna()]

    if len(selected_municipalities) > 0:
        mun_data = data[data["Municipality_name"].isin(selected_municipalities)]

    total_figure = px.line(
        mun_data,
        x="Date_of_report",
        y="Total_reported",
        color="Municipality_name"
    )

    mun_data.sort_values(by=["Municipality_name", "Date_of_report"], inplace=True)

    mun_data["Daily_reported"] = mun_data.groupby("Municipality_name")["Total_reported"].transform(
        lambda x: x.diff()
    )

    if moving_avg not in [None, 0, 1]:
        mun_data["Daily_reported"] =\
            mun_data.groupby("Municipality_name")["Daily_reported"].transform(
                lambda x: x.rolling(
                            window=moving_avg,
                            min_periods=1,
                            center=True
                        ).mean()
            )

    daily_figure = px.line(
        mun_data,
        x="Date_of_report",
        y="Daily_reported",
        color="Municipality_name"
    )

    return (daily_figure, total_figure)


@app.callback(
    Output('daily_province_figure', 'figure'),
    Input('selected_provinces', 'value'),
    Input('moving_avg_province', 'value'),
)
def generate_data_province_wise(selected_provinces, moving_avg):
    data = pd.read_csv(DATA_FILENAME, sep=';')
    data = data[data["Municipality_name"] != ""]
    data = data[data["Municipality_name"].notna()]

    print("Selected provinces:", selected_provinces)

    if len(selected_provinces) > 0:
        data = data[data["Province"].isin(selected_provinces)]

    data.sort_values(by=["Municipality_name", "Date_of_report"], inplace=True)

    data["Daily_reported"] = data.groupby("Municipality_name")["Total_reported"].transform(
        lambda x: x.diff()
    )

    if moving_avg not in [None, 0, 1]:
        data["Daily_reported"] =\
            data.groupby("Municipality_name")["Daily_reported"].transform(
                lambda x: x.rolling(
                            window=moving_avg,
                            min_periods=1,
                            center=True
                        ).mean()
            )

    data_by_province = data.groupby(["Province", "Date_of_report"]).agg({"Daily_reported": sum})
    data_by_province = data_by_province.reset_index()

    daily_province_figure = px.line(
        data_by_province,
        x="Date_of_report",
        y="Daily_reported",
        color="Province"
    )
    return daily_province_figure


def main():
    APP_HOST = "0.0.0.0"
    APP_PORT = 5005
    MODE = sys.argv[1].lower()

    if MODE == "dev":
        app.run_server(debug=True, host=APP_HOST, port=APP_PORT)
    elif MODE == "deploy":
        waitress.serve(app.server, host=APP_HOST, port=APP_PORT, threads=8)
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
