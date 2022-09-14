"""Dashball utilities."""
from datetime import date
from datetime import datetime
from typing import Union

import streamlit as st
from pybaseball import playerid_reverse_lookup
from pybaseball import statcast


@st.cache()
def get_data(game_date: datetime, team: str):

    # Download data
    print("Loading data from statcast... ")
    game_date = dtx(game_date, "str10")
    data = statcast(start_dt=game_date, end_dt=game_date, team=team)
    data = data.rename(columns={"player_name": "pitcher_name"})

    print("Adding batter names... ")
    batter_ids = data["batter"].unique()
    batters = playerid_reverse_lookup(batter_ids, key_type="mlbam")
    batters["batter_name"] = (
        batters["name_first"].str.capitalize()
        + " "
        + batters["name_last"].str.capitalize()
    )

    data = data.merge(
        batters[["key_mlbam", "batter_name"]],
        how="left",
        left_on="batter",
        right_on="key_mlbam",
    )

    data["at_bats"] = data["at_bat_number"] + " " + data["batter_name"]

    data = data.sort_values("at_bat_number")

    return data


def team_name():
    """Get a dictionary with team codes and names."""
    return {
        "ARI": "Arizona Diamonbacks",
        "ATL": "Atlanta Braves",
        "BAL": "Baltimore Orioles",
        "BOS": "Boston Red Sox",
        "CHC": "Chicago Cubs",
        "CIN": "Cincinnati Reds",
        "CLE": "Cleveland Indians",
        "COL": "Colorado Rockies",
        "CWS": "Chicago White Sox",
        "DET": "Detroit Tigers",
        "HOU": "Houston Astros",
        "KC": "Kansas City Royals",
        "LAA": "Los Angeles Angels",
        "LAD": "Los Angeles Dodgers",
        "MIA": "Miami Marlins",
        "MIL": "Milwaukee Brewers",
        "MIN": "Minnesota Twins",
        "NYM": "New York Mets",
        "NYY": "New York Yankees",
        "OAK": "Oakland Athletics",
        "PHI": "Philadelphia Phillies",
        "PIT": "Pittsburgh Pirates",
        "SD": "San Diego Padres",
        "SEA": "Seattle Mariners",
        "SF": "San Francisco Giants",
        "STL": "St. Louis Cardinals",
        "TB": "Tampa Bay Rays",
        "TEX": "Texas Rangers",
        "TOR": "Toronto Blue Jays",
        "WSH": "Washington Nationals",
    }


def dtx(
    in_date: Union[str, date, datetime],
    out_type: str = "sql10",
    in_fmt: str = None,
) -> Union[str, date, datetime]:
    """
    Converts a date with a standardish type into many other types.

    The default is to return a date string that can be used in a SQL query to filter
    by dates, e.g., '2022-06-23' (includes the quotes).

    Args:
        in_date: Type should be date, datetime, or a str like yyyy-mm-dd
            (`%Y-%m-%d`), yyyymmdd (`%Y%m%d`), or another format specified with in_fmt.
        out_type: "date", "datetime", "str10" (yyyy-mm-dd), "str8" (yyyymmdd), or a
            another date format string like "%b-%Y". Use "sql10" and "sql8" to add
            single quotes surrounding the date.

    Returns:
        The date in the specified output type and format.

    """
    if in_date is None:
        return None
    # convert to date type
    # first convert str to datetime, then datetime to date
    if isinstance(in_date, str):
        if in_fmt is not None:
            in_date = datetime.strptime(in_date, in_fmt).date()
        elif len(in_date) == 8:
            in_date = datetime.strptime(in_date, "%Y%m%d").date()
        elif len(in_date) == 10:
            in_date = datetime.strptime(in_date, "%Y-%m-%d").date()
        else:
            raise ValueError
    if isinstance(in_date, datetime):
        in_date = in_date.date()
    # then convert to output type
    if out_type == "date":
        return in_date
    elif out_type == "datetime":
        return datetime(in_date.year, in_date.month, in_date.day)
    elif out_type == "str8":
        return in_date.strftime("%Y%m%d")
    elif out_type == "str10":
        return in_date.strftime("%Y-%m-%d")
    elif out_type == "sql8":
        return in_date.strftime("'%Y%m%d'")
    elif out_type == "sql10":
        return in_date.strftime("'%Y-%m-%d'")
    elif isinstance(out_type, str):
        return in_date.strftime(out_type)
    raise ValueError
