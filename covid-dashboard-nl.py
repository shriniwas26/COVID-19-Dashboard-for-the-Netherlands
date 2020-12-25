import datetime
import json
import sys
import time
import re
import difflib

import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.figure_factory as ff
import scipy
import waitress
from dash.dependencies import Input, Output

# Tick format based on zoom level
TICKFORMAT_STOPS = [
    dict(dtickrange=[None, 1000], value="%H:%M:%S.%L"),
    dict(dtickrange=[1000, 60000], value="%H:%M:%S"),
    dict(dtickrange=[60000, 3600000], value="%H:%M<br>%d-%b"),
    dict(dtickrange=[3600000, 86400000], value="%H:%M<br>%d-%b"),
    dict(dtickrange=[86400000, 604800000], value="%d-%b<br>%Y"),
    dict(dtickrange=[604800000, "M1"], value="%d-%b<br>%Y"),
    dict(dtickrange=["M1", "M12"], value="%b '%Y"),
    dict(dtickrange=["M12", None], value="%Y Y")
]


app = dash.Dash(__name__, url_base_pathname='/covid-nl/',
                assets_folder='assets')
app.title = "COVID-19 Dashboard - The Netherlands"

DATA_FILENAME = "COVID-19_aantallen_gemeente_cumulatief.csv"

initial_read = pd.read_csv(DATA_FILENAME, sep=';')
initial_read = initial_read[initial_read["Municipality_name"] != ""]
initial_read = initial_read[initial_read["Municipality_name"].notna()]

# Read population data
pop_data = pd.read_csv("Netherlands_population.csv")
pop_data["Name"] = pop_data["Name"].apply(lambda x: x.replace("\xa0", ""))
pop_data["Name"] = pop_data["Name"].apply(lambda x: re.sub(r"\(.+\)", "", x))
pop_data["Name"] = pop_data["Name"].apply(lambda x: re.sub(r"\s+$", "", x))
pop_data = pop_data.rename(
    columns={"Population Estimate 2020-01-01": "Population"})

# Extract municipality population data
mun_pop_data = pop_data[pop_data["Status"] == "Municipality"]
mun_pop_data = mun_pop_data.rename(columns={"Name": "Municipality_name"})

# Extract province population data
prov_pop_data = pop_data[pop_data["Status"] == "Province"]
prov_pop_data = prov_pop_data.rename(columns={"Name": "Province"})
prov_pop_data["Province"] = prov_pop_data["Province"].apply(
            lambda x: difflib.get_close_matches(x, initial_read['Province'].unique())[0])


unique_municipalities = set(initial_read["Municipality_name"]) & set(
    mun_pop_data["Municipality_name"])
unique_provinces = set(initial_read["Province"])


app.layout = html.Div([
    html.Div([
        html.H6("Select municipalities:"),
        dcc.Dropdown(
            id='selected_municipalities',
            options=[{'label': i, 'value': i}
                     for i in sorted(unique_municipalities)],
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
        'width': '40%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px',
        'height': '100%',
    }),
    html.Div([
        html.H6("Moving average (days)"),
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
                'vertical-align': 'top',
                'textAlign': 'left',
                'border-radius': '25px',
                'margin-left': '30%',
                'margin-right': '30%',
                'width': '40%',
            }
        ),
        html.Br(),
        html.Br()
    ], style={
        'width': '15%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px',
        'height': '100%',
    }),
    html.Div([
        html.H6("Data type:"),
        dcc.RadioItems(
            id='data_type',
            options=[{'label': i, 'value': i}
                     for i in ["Absolute", "Per 10k people"]],
            value="Absolute",
            style={
                'textAlign': 'left',
                'align': 'center',
                'border-radius': '25px',
                'margin-left': '5%',
                'width': '90%'
            },
        ),
        html.Br(),
    ], style={
        'width': '12%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px',
        'height': '100%',
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
            value=sorted(
                ['Zuid-Holland', 'Noord-Brabant', 'Utrecht', 'Limburg']),
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
        'width': '40%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px'
    }),
    html.Div([
        html.H6("Moving average (days)"),
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
                'vertical-align': 'top',
                'textAlign': 'left',
                'border-radius': '25px',
                'margin-left': '30%',
                'margin-right': '30%',
                'width': '40%',
            }
        ),
        html.Br(),
        html.Br()
    ], style={
        'width': '15%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px'
    }),
    html.Div([
        html.H6("Data type:"),
        dcc.RadioItems(
            id='data_type_prov',
            options=[{'label': i, 'value': i}
                     for i in ["Absolute", "Per 10k people"]],
            value="Absolute",
            style={
                'textAlign': 'left',
                'align': 'center',
                'border-radius': '25px',
                'margin-left': '5%',
                'width': '90%'
            },
        ),
        html.Br(),
    ], style={
        'width': '12%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'textAlign': 'center',
        'border': '2px black solid',
        'border-radius': '25px',
        'margin': '5px',
        'height': '100%',
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
    html.Div([
        dcc.Graph(
            id='total_province_figure',
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
    Input('data_type', 'value'),
)
def generate_data(selected_municipalities, moving_avg, data_type):
    data = pd.read_csv(DATA_FILENAME, sep=';')
    data = data[data["Municipality_name"] != ""]
    data = data[data["Municipality_name"].notna()]

    if len(selected_municipalities) > 0:
        mun_data = data[data["Municipality_name"].isin(
            selected_municipalities)]

    mun_data.sort_values(
        by=["Municipality_name", "Date_of_report"], inplace=True)

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

    if data_type == "Per 10k people":
        mun_data = mun_data.merge(mun_pop_data)
        mun_data["Daily_reported"] = mun_data["Daily_reported"] / \
            mun_data["Population"] * 1E4
        mun_data["Total_reported"] = mun_data["Total_reported"] / \
            mun_data["Population"] * 1E4

    daily_figure = px.line(
        mun_data,
        x="Date_of_report",
        y="Daily_reported",
        color="Municipality_name"
    )
    daily_figure.update_yaxes(title_text="Daily reported")
    daily_figure.update_xaxes(title_text="Date of report")

    total_figure = px.line(
        mun_data,
        x="Date_of_report",
        y="Total_reported",
        color="Municipality_name"
    )
    total_figure.update_yaxes(title_text="Total reported")
    total_figure.update_xaxes(title_text="Date of report")

    for fig in [daily_figure, total_figure]:
        fig.update_layout(
            xaxis_tickformatstops=TICKFORMAT_STOPS
        )

    return (daily_figure, total_figure)


@app.callback(
    Output('daily_province_figure', 'figure'),
    Output('total_province_figure', 'figure'),
    Input('selected_provinces', 'value'),
    Input('moving_avg_province', 'value'),
    Input('data_type_prov', 'value'),
)
def generate_data_province_wise(selected_provinces, moving_avg, data_type_prov):
    data = pd.read_csv(DATA_FILENAME, sep=';')
    data = data[data["Municipality_name"] != ""]
    data = data[data["Municipality_name"].notna()]

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

    data_by_province = data.groupby(
        ["Province", "Date_of_report"]).agg({"Daily_reported": sum, "Total_reported": sum})
    data_by_province = data_by_province.reset_index()

    if data_type_prov == "Per 10k people":
        data_by_province = data_by_province.merge(prov_pop_data)
        data_by_province["Daily_reported"] = data_by_province["Daily_reported"] / \
            data_by_province["Population"] * 1E4
        data_by_province["Total_reported"] = data_by_province["Total_reported"] / \
            data_by_province["Population"] * 1E4

    daily_province_figure = px.line(
        data_by_province,
        x="Date_of_report",
        y="Daily_reported",
        color="Province"
    )
    daily_province_figure.update_yaxes(title_text="Daily reported")
    daily_province_figure.update_xaxes(title_text="Date of report")

    daily_province_figure.update_layout(
        xaxis_tickformatstops=TICKFORMAT_STOPS
    )

    total_province_figure = px.line(
        data_by_province,
        x="Date_of_report",
        y="Total_reported",
        color="Province"
    )
    total_province_figure.update_yaxes(title_text="Total reported")
    total_province_figure.update_xaxes(title_text="Date of report")

    total_province_figure.update_layout(
        xaxis_tickformatstops=TICKFORMAT_STOPS
    )

    return daily_province_figure, total_province_figure


def main():
    if "--dev" in sys.argv[1:]:
        app.run_server(debug=True, host=APP_HOST, port=APP_PORT)
    else:
        waitress.serve(app.server, host=APP_HOST, port=APP_PORT, threads=8)


if __name__ == "__main__":
    APP_HOST = "127.0.0.1"
    APP_PORT = 5005
    sys.exit(main())
