"""Dashball: Dashboard for baseball."""

import os
from datetime import datetime as dt

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

from dash_utils import dcc_dropdown_div
from utils import team_name

# print("Loading data... ", end="")
filename = "./statcast.parquet"
raw = pd.read_parquet(filename)
raw = raw.rename(columns={"player_name": "pitcher_name"})
# print("Done.")

# print("Adding batter names... ", end="")

batters_filename = "./playerid_lookup_table.csv"
ids = pd.read_csv(batters_filename)

ids["batter_name"] = (
    ids["name_first"].str.capitalize()
    + " "
    + ids["name_last"].str.capitalize()
)

raw = raw.merge(
    ids[["key_mlbam", "batter_name"]],
    how="left",
    left_on="batter",
    right_on="key_mlbam",
)

# print("Done.")

# TODO: add batter_team

home_teams = list(raw["home_team"].unique())
away_teams = list(raw["away_team"].unique())
teams = home_teams + away_teams  # TODO: sort by name
innings = list(raw["inning"].sort_values().unique())

# build the app
app = dash.Dash(__name__)
app.layout = html.Div(
    id="container",
    children=[
        html.H1(children="Dashball"),
        dcc.DatePickerSingle(
            id="date-picker",
            min_date_allowed=dt(2013, 1, 1),
            max_date_allowed=dt(2019, 12, 31),
            initial_visible_month=dt(2019, 7, 1),
            date=str(dt(2019, 7, 1)),
        ),
        dcc_dropdown_div(
            id="team-dropdown",
            title="Team:",
            opts=team_name(),
            value="TOR",
        ),
        dcc.Dropdown(
            id="inning-dropdown",
            options=[{"label": x, "value": x} for x in innings],
            value=1,
        ),
        dcc.Dropdown(id="batter-dropdown"),
        dcc.Graph(id="pitch-locations"),
    ],
)


@app.callback(
    Output("batter-dropdown", "options"),
    [
        Input("date-picker", "date"),
        Input("team-dropdown", "value"),
        Input("inning-dropdown", "value"),
    ],
)
def _update_batter_dropdown(date, team, inning):
    team_col = "home_team" if team in home_teams else "away_team"
    df = raw[raw["game_date"] == date]
    df = df[df[team_col] == team]
    df = df[df["inning"] == inning]
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
        Input("date-picker", "date"),
        Input("team-dropdown", "value"),
        Input("inning-dropdown", "value"),
        Input("batter-dropdown", "value"),
    ],
)
def _update_pitch_locations(date, team, inning, at_bat_number):
    team_col = "home_team" if team in home_teams else "away_team"
    df = raw[raw["game_date"] == date]
    df = df[df[team_col] == team]
    df = df[df["inning"] == inning]
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
