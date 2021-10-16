import difflib
import re
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
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


COVID_DATA = initial_read.copy()
METRICS = [
    'Total_reported', 'Hospital_admission', 'Deceased'
]
COVID_DATA.sort_values(by=["Municipality_code", "Date_of_report"])

## Compute daily values ##
for feat in METRICS:
    COVID_DATA[f"Daily_{feat}"] = COVID_DATA.groupby("Municipality_name")[feat].transform(
        lambda x: x.diff().fillna(0)
    )
    COVID_DATA[f"Daily_{feat}"] = np.clip(
        COVID_DATA[f"Daily_{feat}"], a_min=0, a_max=None)


# Aggregate data per province
PROVINCE_COLS = [f"Daily_{m}" for m in METRICS] + METRICS
PROVINCIAL_COVID_DATA = COVID_DATA.groupby(["Province", "Date_of_report"]).agg(
    {metric: np.sum for metric in PROVINCE_COLS})
PROVINCIAL_COVID_DATA = PROVINCIAL_COVID_DATA.reset_index()


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
        html.H6("Metric:"),
        dcc.Dropdown(
            id='covid_metric',
            options=[{'label': i, 'value': i}
                     for i in METRICS],
            value=METRICS[0],
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
        html.H6("Moving avg. (days)"),
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
            value="Per 10k people",
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
    Input('covid_metric', 'value'),
    Input('moving_avg', 'value'),
    Input('data_type', 'value'),
)
def generate_data(selected_municipalities, covid_metric, moving_avg, data_type):
    selected_municipalities = sorted(selected_municipalities)

    if len(selected_municipalities) > 0:
        mun_data = COVID_DATA[COVID_DATA["Municipality_name"].isin(
            selected_municipalities)].copy()
    else:
        random_municipalities = np.random.choice(
            list(unique_municipalities), size=5)
        mun_data = COVID_DATA[COVID_DATA["Municipality_name"].isin(
            random_municipalities)].copy()

    mun_data.sort_values(
        by=["Municipality_name", "Date_of_report"], inplace=True)

    if moving_avg not in [None, 0, 1]:
        mun_data[f"Daily_{covid_metric}"] =\
            mun_data.groupby("Municipality_name")[f"Daily_{covid_metric}"].transform(
                lambda x: x.rolling(
                    window=int(moving_avg),
                    min_periods=1,
                    center=False
                ).mean()
        )

    if data_type == "Per 10k people":
        mun_data = mun_data.merge(mun_pop_data)
        mun_data[f"Daily_{covid_metric}"] = (
            mun_data[f"Daily_{covid_metric}"] / mun_data["Population"] * 1E4
        )
        mun_data[covid_metric] = (
            mun_data[covid_metric] / mun_data["Population"] * 1E4
        )

    daily_figure = px.line(
        mun_data,
        x="Date_of_report",
        y=f"Daily_{covid_metric}",
        color="Municipality_name",
    )
    daily_figure.update_yaxes(
        title_text=f"Daily {covid_metric} ({data_type})".replace("_", " "))
    daily_figure.update_xaxes(title_text="Date of report")


    total_figure = px.line(
        mun_data,
        x="Date_of_report",
        y=covid_metric,
        color="Municipality_name",
    )
    total_figure.update_yaxes(
        title_text=f"{covid_metric} ({data_type})".replace("_", " "))
    total_figure.update_xaxes(title_text="Date of report")
    total_figure.update_layout(
        xaxis_tickformatstops=TICKFORMAT_STOPS
    )

    return (daily_figure, total_figure)


@app.callback(
    Output('daily_province_figure', 'figure'),
    Output('total_province_figure', 'figure'),
    Input('selected_provinces', 'value'),
    Input('covid_metric', 'value'),
    Input('moving_avg', 'value'),
    Input('data_type', 'value'),
)
def generate_data_province_wise(selected_provinces, covid_metric, moving_avg, data_type):
    if len(selected_provinces) > 0:
        province_data_selected = PROVINCIAL_COVID_DATA[PROVINCIAL_COVID_DATA["Province"].isin(
            selected_provinces)].copy()
    else:
        province_data_selected = PROVINCIAL_COVID_DATA.copy()

    if data_type == "Per 10k people":
        province_data_selected = province_data_selected.merge(
            prov_pop_data, on="Province")
        province_data_selected[f"Daily_{covid_metric}"] = (
            province_data_selected[f"Daily_{covid_metric}"] /
            province_data_selected["Population"] * 1E4
        )
        province_data_selected[covid_metric] = province_data_selected[covid_metric] / \
            province_data_selected["Population"] * 1E4

    if moving_avg not in [None, 0, 1]:
        province_data_selected[f"Daily_{covid_metric}"] =\
            province_data_selected.groupby("Province")[f"Daily_{covid_metric}"].transform(
                lambda x: x.rolling(
                    window=int(moving_avg),
                    min_periods=1,
                    center=False
                )
                .mean()
        )

    daily_province_figure = px.line(
        province_data_selected,
        x="Date_of_report",
        y=f"Daily_{covid_metric}",
        color="Province"
    )
    daily_province_figure.update_yaxes(
        title_text=f"Daily {covid_metric} ({data_type})".replace("_", " "))
    daily_province_figure.update_xaxes(title_text="Date of report")
    daily_province_figure.update_layout(
        xaxis_tickformatstops=TICKFORMAT_STOPS
    )

    total_province_figure = px.line(
        province_data_selected,
        x="Date_of_report",
        y=covid_metric,
        color="Province"
    )
    total_province_figure.update_yaxes(
        title_text=f"{covid_metric} ({data_type})".replace("_", " "))
    total_province_figure.update_xaxes(title_text="Date of report")
    total_province_figure.update_layout(
        xaxis_tickformatstops=TICKFORMAT_STOPS
    )

    return (daily_province_figure, total_province_figure)


def main():
    if "--dev" in sys.argv[1:]:
        app.run_server(debug=True, host=APP_HOST, port=APP_PORT)
    else:
        waitress.serve(app.server, host=APP_HOST, port=APP_PORT, threads=8)


if __name__ == "__main__":
    APP_HOST = "127.0.0.1"
    APP_PORT = 5005
    sys.exit(main())
