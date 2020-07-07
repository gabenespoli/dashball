# %run statcast.py

import os
from datetime import datetime as dt

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output


# print("Loading data... ", end="")
filename = "/Users/53gnespoli/local/private/data/mlb/statcast.parquet"
raw = pd.read_parquet(filename)
raw = raw.rename(columns={"player_name": "pitcher_name"})
# print("Done.")

# %%
# print("Adding batter names... ", end="")

batters_filename = (
    "/Users/53gnespoli/local/private/data/mlb/playerid_lookup_table.csv"
)
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

# %%
home_teams = list(raw["home_team"].unique())
away_teams = list(raw["away_team"].unique())
teams = home_teams + away_teams  # TODO: sort by name
innings = list(raw["inning"].sort_values().unique())

# %%
# build the app
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.H1(children="Game Day"),
        dcc.DatePickerSingle(
            id="date-picker",
            min_date_allowed=dt(2013, 1, 1),
            max_date_allowed=dt(2019, 12, 31),
            initial_visible_month=dt(2019, 7, 1),
            date=str(dt(2019, 7, 1)),
        ),
        dcc.Dropdown(
            id="team-dropdown",
            options=[{"label": x, "value": x} for x in teams],
            value="TOR" if "TOR" in teams else teams[0],
            style={"width": "40%"},
        ),
        dcc.Dropdown(
            id="inning-dropdown",
            options=[{"label": x, "value": x} for x in innings],
            value=1,
            style={"width": "30%"},
        ),
        dcc.Dropdown(id="batter-dropdown", style={"width": "60%"},),
        dcc.Graph(
            id="pitch-locations",
            style={"width": "75%", "display": "inline-block"},
        ),
    ]
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
        width=800,
        height=800,
        template="plotly_dark",
    )


if __name__ == "__main__":
    app.server.run(port=8051, host='127.0.0.1', debug=True)