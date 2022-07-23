"""Dashball: Dashboard for baseball."""

import os
from datetime import datetime as dt

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import Input
from dash import Output
from dash import dcc
from dash import html
from pybaseball import playerid_reverse_lookup
from pybaseball import statcast

from app import app
from dash_utils import dcc_dropdown_div
from utils import team_name

app.layout = dbc.Container(
    children=[
        dbc.Row(
            dbc.Col(
                html.H1(children="Dashball"),
            ),
        ),
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        html.Label("Date:"),
                        html.Br(),
                        dcc.DatePickerSingle(
                            id="date-picker",
                            initial_visible_month=dt(2019, 7, 1),
                            date=str(dt(2019, 7, 1).strftime("%Y-%m-%d")),
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        "position": "relative",
                    },
                ),
                dbc.Col(
                    dcc_dropdown_div(
                        id="team-dropdown",
                        title="Team:",
                        opts=team_name(),
                        value="TOR",
                    ),
                ),
                dbc.Col(
                    dcc_dropdown_div(
                        id="batter-dropdown",
                        title="Batter:",
                    ),
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id="pitch-locations"),
            ),
        ),
        html.Div(id="data-store", style={"display": "none"}),
    ],
)


@app.callback(
    Output("data-store", "children"),
    [
        Input("date-picker", "date"),
        Input("team-dropdown", "value"),
    ],
)
def update_data(date, team):
    """Load game data using pybaseball's scraper.

    Uses pybaseball.statcast and pybaseball.playerid_reverse_lookup to load
    data from a specific game, and stores it as json in the user's browser
    session in a hidden div.

    """
    print("Loading data from statcast... ")
    raw = statcast(start_dt=date, end_dt=date, team=team)
    raw = raw.rename(columns={"player_name": "pitcher_name"})

    print("Adding batter names... ")
    batter_ids = raw["batter"].unique()
    batters = playerid_reverse_lookup(batter_ids, key_type="mlbam")
    batters["batter_name"] = (
        batters["name_first"].str.capitalize()
        + " "
        + batters["name_last"].str.capitalize()
    )

    raw = raw.merge(
        batters[["key_mlbam", "batter_name"]],
        how="left",
        left_on="batter",
        right_on="key_mlbam",
    )

    print("Done.")

    return raw.to_json(date_format="iso", orient="split")


@app.callback(
    Output("batter-dropdown", "options"),
    [
        Input("data-store", "children"),
    ],
)
def _update_batter_dropdown(json_data):
    # TODO: add batter_team
    df = pd.read_json(json_data, orient="split")
    batters = (
        df[["batter_name", "home_team", "away_team", "at_bat_number"]]
        .sort_values("at_bat_number")
        .drop_duplicates()
    )
    batters = list(
        zip(
            batters["batter_name"] + " (" + batters["home_team"] + ")",
            batters["at_bat_number"],
        )
    )
    return [{"label": str(int(y)) + " " + x, "value": y} for x, y in batters]


@app.callback(
    Output("pitch-locations", "figure"),
    [
        Input("data-store", "children"),
        Input("batter-dropdown", "value"),
    ],
)
def _update_pitch_locations(json_data, at_bat_number):
    df = pd.read_json(json_data, orient="split")
    df = df[df["at_bat_number"] == at_bat_number]
    return px.scatter(
        df,
        x="plate_x",
        y="plate_z",
        # color="type",
        hover_data=[
            "batter_name",
            "pitcher_name",
            "inning",
            "events",
            "stand",
        ],
        range_x=[-3, 3],
        range_y=[0, 6],
        width=500,
        height=500,
    )


if __name__ == "__main__":
    # Get port, host, and debug mode from environment variables
    debug = os.environ.get("dash_debug")
    host = os.environ.get("dash_host")
    port = os.environ.get("dash_port")

    # set defaults so that we can run from command line too
    debug = True if debug == "True" else False
    host = "0.0.0.0" if host is None else host
    port = 8000 if port is None else port

    print(
        "Starting app.run_server(debug={0}, host='{1}', port={2})...".format(
            debug, host, port
        )
    )

    # Run the app
    app.run_server(debug=debug, host=host, port=port)

    print("Done.")
