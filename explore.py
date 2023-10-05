import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
st.title("Baseball der Dashboard")

batflip = pd.read_csv("~/eg/data/mlb/bat_flip_game.csv")
st.write(batflip)


@st.cache()
def get_data(filename, **kwargs):
    data = pd.read_parquet(filename, **kwargs)
    return data


filename = "~/eg/data/mlb/statcast.parquet"
data = get_data(
    filename,
    columns=[
        "player_name",
        "pitch_type",
        "events",
        "description",
        "stand",
        "p_throws",
        "type",
        "bb_type",
        "balls",
        "strikes",
        "home_team",
        "away_team",
        "outs_when_up",
        "inning",
        "inning_topbot",
        "at_bat_number",
        "pitch_number",
        "pitch_name",
        "pitcher",
        "batter",
    ],
)

st.write(data)
