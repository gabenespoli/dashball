from datetime import datetime
from datetime import timedelta

import streamlit as st

import graphs
import utils

# Sidebar filters (pre-downloading data)
game_date = st.sidebar.date_input(
    label="Game Date", value=datetime.today() - timedelta(days=1)
)

teams = list(utils.team_name().keys())
team = st.sidebar.selectbox(
    label="Team",
    options=teams,
    index=teams.index("TOR") if "TOR" in teams else 0,
)

# Download data
data = utils.get_data(game_date, team=team)

# Filters based on downloaded data
at_bat = st.selectbox(label="Batter", options=data["at_bats"].to_list())

st.plotly_chart(graphs.pitch_locations(data, at_bat), use_container_width=True)
