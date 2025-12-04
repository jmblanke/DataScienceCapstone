# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the launch data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),

        # Dropdown for Launch Site selection
        dcc.Dropdown(
            id="site-dropdown",
            options=[{"label": "All Sites", "value": "ALL"}]
            + [
                {"label": site, "value": site}
                for site in spacex_df["Launch Site"].unique()
            ],
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),

        html.Br(),

        # Pie chart for launch success
        html.Div(dcc.Graph(id="success-pie-chart")),

        html.Br(),

        html.P("Payload range (Kg):"),

        # RangeSlider for payload
        dcc.RangeSlider(
            id="payload-slider",
            min=min_payload,
            max=max_payload,
            step=1000,
            marks={
                int(min_payload): str(int(min_payload)),
                int(max_payload): str(int(max_payload)),
            },
            value=[min_payload, max_payload],
        ),

        # Scatter chart for payload vs success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# Callback for pie chart
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        # Show total successful launches by site
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Success Launches by Site",
        )
    else:
        # Filter data for the selected launch site
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]

        # Count success (1) and failure (0)
        success_counts = filtered_df["class"].value_counts().reset_index()
        success_counts.columns = ["class", "count"]

        # Map class values to labels
        success_counts["class"] = success_counts["class"].map(
            {1: "Success", 0: "Failure"}
        )

        fig = px.pie(
            success_counts,
            values="count",
            names="class",
            title=f"Success vs Failure for site {entered_site}",
        )

    return fig


# Callback for scatter chart
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range

    # Base mask for payload range
    mask = (spacex_df["Payload Mass (kg)"] >= low) & (
        spacex_df["Payload Mass (kg)"] <= high
    )

    if selected_site == "ALL":
        filtered_df = spacex_df[mask]
        title = "Payload vs Outcome for All Sites"
    else:
        mask = mask & (spacex_df["Launch Site"] == selected_site)
        filtered_df = spacex_df[mask]
        title = f"Payload vs Outcome for site {selected_site}"

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=title,
        labels={"class": "Launch Outcome"},
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
