import plotly.express as px

def pitch_locations(data, at_bat):
    dp = data[data["at_bats"] == at_bat]
    fig = px.scatter(
        dp,
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
    return fig
