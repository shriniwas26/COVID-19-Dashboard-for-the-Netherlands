import datetime
import sys

import dash
import dash.dcc as dcc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import html
from dash.dependencies import Input, Output

PER_POPULATION = 100


def round_significant_digits(x, n=2):
    if type(x) in [int, float]:
        if x == 0:
            return 0
        if x > 1:
            return round(x, n)

    power = 10 ** np.ceil(np.log10(abs(x)))
    return round(x / power, n) * power


## Metrics to display ##
METRICS = ['Total_reported', 'Hospital_admission', 'Deceased']

## Initial reading and sanitization steps ##
try:
    COVID_DATA = pd.read_csv(
        "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv",
        sep=";"
    )
except:
    print("Cannot read url, reading locally.")
    COVID_DATA = pd.read_csv(
        "data/COVID-19_aantallen_gemeente_cumulatief.csv",
        sep=";"
    )
COVID_DATA["Date_of_report"] = pd.to_datetime(COVID_DATA["Date_of_report"])


## Replace faulty data ##
COVID_DATA["Province"] = COVID_DATA["Province"].replace(
    {"FryslÃ¢n": 'Friesland'}
)


# Remove all data points which don't have a municipality name
COVID_DATA = COVID_DATA[COVID_DATA["Municipality_name"] != ""]
COVID_DATA = COVID_DATA[(COVID_DATA["Municipality_name"].notna())]


##  Read population data ##
mun_population_data = pd.read_csv("data/NL_Population_Latest.csv")
mun_population_data = mun_population_data.rename(columns={
    "PopulationOn31December_20": "Population"
})


## Merge the population data ##
COVID_DATA = COVID_DATA.merge(
    mun_population_data,
    left_on="Municipality_code",
    right_on="Regions",
    how="inner"
)

## Compute daily values ##
COVID_DATA = COVID_DATA.sort_values(
    by=["Municipality_code", "Municipality_name", "Date_of_report"]
)
for metric in METRICS:
    COVID_DATA[f"Daily_{metric}"] = COVID_DATA.groupby("Municipality_name")[metric].transform(
        lambda x: x.diff().fillna(0)
    )


## Aggregate data per province ##
PROVINCE_COLS = [
    f"Daily_{metric}" for metric in METRICS] + METRICS + ["Population"]
PROVINCIAL_COVID_DATA = COVID_DATA.groupby(["Province", "Date_of_report"]).agg(
    {col: np.sum for col in PROVINCE_COLS}
).reset_index()


## Calculate unique municipalities which have both population and covid data ##
UNIQUE_MUNICIPALITIES = np.unique(COVID_DATA["Municipality_name"])
UNIQUE_PROVINCES = np.unique(COVID_DATA["Province"])


## Setup the dash app ##
app = dash.Dash(
    __name__,
    assets_folder='assets'
)
app.title = "COVID-19 Dashboard - The Netherlands"
server = app.server

app.layout = html.Div([
    html.Div([
        html.H6("Select municipalities:"),
        dcc.Dropdown(
            id='selected_municipalities',
            options=[
                {'label': i, 'value': i}
                for i in sorted(UNIQUE_MUNICIPALITIES)
            ],
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
            options=[{'label': i.replace("_", " "), 'value': i}
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
            max=100,
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
            options=[
                {'label': i, 'value': i}
                for i in ["Absolute", "Population Adjusted"]
            ],
            value="Population Adjusted",
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
            options=[{'label': i, 'value': i} for i in UNIQUE_PROVINCES],
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
    [
        Output('daily_figure', 'figure'),
        Output('total_figure', 'figure'),
    ],
    [
        Input('selected_municipalities', 'value'),
        Input('covid_metric', 'value'),
        Input('moving_avg', 'value'),
        Input('data_type', 'value'),
    ]
)
def process_and_render_muns(selected_municipalities, covid_metric, moving_avg, data_type):
    selected_municipalities = sorted(selected_municipalities)

    if len(selected_municipalities) > 0:
        mun_data = COVID_DATA[COVID_DATA["Municipality_name"].isin(
            selected_municipalities)].copy()
    else:
        return go.Figure(), go.Figure()

    if moving_avg not in [None, 0, 1]:
        mun_data[f"Daily_{covid_metric}"] =\
            mun_data.groupby("Municipality_name")[f"Daily_{covid_metric}"].transform(
                lambda x: x[::-1].rolling(
                    window=int(moving_avg),
                    min_periods=1,
                    center=False
                )
                .mean()[::-1]
        )

    if data_type == "Population Adjusted":
        mun_data[f"Daily_{covid_metric}"] = (
            mun_data[f"Daily_{covid_metric}"] / mun_data["Population"] * 100
        )
        mun_data[covid_metric] = (
            mun_data[covid_metric] / mun_data["Population"] * 100
        )

    ## Round the data to 3 significant digits ##
    mun_data[f"Daily_{covid_metric}"] = mun_data[f"Daily_{covid_metric}"].apply(
        lambda x: round_significant_digits(x, 3))
    mun_data[covid_metric] = mun_data[covid_metric].apply(
        lambda x: round_significant_digits(x, 3))

    ## Add figure for daily numbers ##
    daily_mun_figure = go.Figure()
    for grp, df in mun_data.groupby("Municipality_name"):
        daily_mun_figure.add_trace(
            go.Scatter(
                x=df["Date_of_report"],
                y=df[f"Daily_{covid_metric}"],
                name=grp,
                mode="markers+lines",
                line_shape="spline",
                marker={"size": 2},
                hovertemplate="%{x}<br>%{y}",
            )
        )
    daily_mun_figure.update_layout(
        title=f"Daily {covid_metric} ({data_type})"
        .title()
        .replace("_", " ")
        .replace("Population Adjusted", f"per {PER_POPULATION} people"),
        title_x=0.5,
    )
    daily_mun_figure.update_xaxes(title="Date of report")

    ## Add figure for total numbers ##
    total_mun_figure = go.Figure()
    for grp, df in mun_data.groupby("Municipality_name"):
        total_mun_figure.add_trace(
            go.Scatter(
                x=df["Date_of_report"],
                y=df[covid_metric],
                name=grp,
                mode="markers+lines",
                line_shape="spline",
                marker={"size": 2},
                hovertemplate="%{x}<br>%{y}",
            )
        )
    total_mun_figure.update_yaxes(title_text="")
    total_mun_figure.update_xaxes(title_text="Date of report")
    total_mun_figure.update_layout(
        title=f"{covid_metric} ({data_type})"
        .title()
        .replace("_", " ")
        .replace("Population Adjusted", f"per {PER_POPULATION} people"),
        title_x=0.5,
    )

    return (daily_mun_figure, total_mun_figure)


@app.callback(
    [
        Output('daily_province_figure', 'figure'),
        Output('total_province_figure', 'figure'),
    ],
    [
        Input('selected_provinces', 'value'),
        Input('covid_metric', 'value'),
        Input('moving_avg', 'value'),
        Input('data_type', 'value'),
    ]
)
def process_and_render_provinces(selected_provinces, covid_metric, moving_avg, data_type):
    if len(selected_provinces) > 0:
        province_data_selected = PROVINCIAL_COVID_DATA[PROVINCIAL_COVID_DATA["Province"].isin(
            selected_provinces)].copy()
    else:
        province_data_selected = PROVINCIAL_COVID_DATA.copy()

    if data_type == "Population Adjusted":
        province_data_selected[f"Daily_{covid_metric}"] = (
            province_data_selected[f"Daily_{covid_metric}"] /
            province_data_selected["Population"] * 100
        )
        province_data_selected[covid_metric] = (
            province_data_selected[covid_metric] /
            province_data_selected["Population"] * 100
        )

    if moving_avg not in [None, 0, 1]:
        province_data_selected[f"Daily_{covid_metric}"] =\
            province_data_selected.groupby("Province")[f"Daily_{covid_metric}"].transform(
            lambda x: x[::-1].rolling(
                window=int(moving_avg),
                min_periods=1,
                center=False
            )
            .mean()[::-1]
        )

    province_data_selected[f"Daily_{covid_metric}"] = province_data_selected[f"Daily_{covid_metric}"].apply(
        round_significant_digits)
    province_data_selected[covid_metric] = province_data_selected[covid_metric].apply(
        round_significant_digits)

    daily_province_figure = go.Figure()
    for grp, df in province_data_selected.groupby("Province"):
        daily_province_figure.add_trace(
            go.Scatter(
                x=df["Date_of_report"],
                y=df[f"Daily_{covid_metric}"],
                name=grp,
                mode="markers+lines",
                line_shape="spline",
                marker={"size": 2},
                hovertemplate="%{x}<br>%{y}",
            )
        )
    daily_province_figure.update_xaxes(title_text="Date of report")
    daily_province_figure.update_yaxes(title_text="")
    daily_province_figure.update_layout(
        title=f"Daily {covid_metric} ({data_type})"
        .title()
        .replace("_", " ")
        .replace("Population Adjusted", f"per {PER_POPULATION} people"),
        title_x=0.5,
    )

    total_province_figure = go.Figure()
    for grp, df in province_data_selected.groupby("Province"):
        total_province_figure.add_trace(
            go.Scatter(
                x=df["Date_of_report"],
                y=df[covid_metric],
                name=grp,
                mode="markers+lines",
                line_shape="spline",
                marker={"size": 2},
                hovertemplate="%{x}<br>%{y}",
            )
        )
    total_province_figure.update_xaxes(title_text="Date of report")
    total_province_figure.update_yaxes(title_text="")
    total_province_figure.update_layout(
        title=f"{covid_metric} ({data_type})"
        .title()
        .replace("_", " ")
        .replace("Population Adjusted", f"per {PER_POPULATION} people"),
        title_x=0.5,
    )

    return (daily_province_figure, total_province_figure)


def main():
    APP_PORT = 5005
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"Starting dashboard for COVID-19 data in The Netherlands at {time_now}")
    app.run_server(
        debug=True,
        host="0.0.0.0",
        port=APP_PORT
    )


if __name__ == "__main__":
    sys.exit(main())
