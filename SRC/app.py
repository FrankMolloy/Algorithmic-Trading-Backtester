from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

from simulator import simulate
from metrics import summarise, prob_reach_goal

scenarios = {
    "cautious":  {"r": 0.05, "vol": 0.10},
    "balanced":  {"r": 0.07, "vol": 0.15},
    "aggressive":{"r": 0.09, "vol": 0.20},
}

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "RiskWise"

def money(x: float) -> str:
    return f"£{x:,.0f}"

app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col([
            html.H2("RiskWise", className="mt-3"),
            html.P("A Monte Carlo financial simulator that visualises uncertainty, inflation effects, and goal probability.", className="text-muted"),
        ], width=8),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Inputs", className="card-title"),

                    html.Label("Scenario", className="mt-2"),
                    dcc.Dropdown(
                        options=[{"label": k.title(), "value": k} for k in scenarios.keys()],
                        value="balanced",
                        id="scenario",
                        clearable=False
                    ),

                    html.Label("Years", className="mt-3"),
                    dcc.Slider(1, 40, 1, value=10, id="years",
                               marks={1:"1", 10:"10", 20:"20", 30:"30", 40:"40"}),

                    html.Label("Monthly Contribution", className="mt-3"),
                    dcc.Slider(0, 2000, 50, value=200, id="monthly",
                               marks={0:"0", 500:"500", 1000:"1000", 1500:"1500", 2000:"2000"}),

                    html.Label("Goal (£)", className="mt-3"),
                    dbc.Input(type="number", value=50000, id="goal", min=0, step=1000),

                    html.Hr(),

                    html.Div(id="stats-cards")
                ])
            ], className="shadow-sm")
        ], width=4),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Simulated Paths", className="card-title"),
                    dcc.Graph(id="paths-graph", config={"displayModeBar": False})
                ])
            ], className="shadow-sm mb-3"),

            dbc.Card([
                dbc.CardBody([
                    html.H5("Outcome Distribution", className="card-title"),
                    dcc.Graph(id="hist-graph", config={"displayModeBar": False})
                ])
            ], className="shadow-sm")
        ], width=8),
    ], className="mt-3 mb-4")
])

@app.callback(
    Output("paths-graph", "figure"),
    Output("hist-graph", "figure"),
    Output("stats-cards", "children"),
    Input("scenario", "value"),
    Input("years", "value"),
    Input("monthly", "value"),
    Input("goal", "value"),
)
def update_graph(scenario, years, monthly, goal):
    params = scenarios[scenario]

    # keep UI responsive
    paths = simulate(
        years=years,
        start_balance=1000,
        monthly_contribution=monthly,
        expected_return_annual=params["r"],
        volatility_annual=params["vol"],
        inflation_annual=0.02,
        simulations=2000,
        seed=42
    )

    final_values = paths[:, -1]
    summary = summarise(final_values)
    p_goal = prob_reach_goal(final_values, goal if goal else 0)

    # ----- Paths plot (plot a small sample) -----
    fig_paths = go.Figure()
    sample_n = min(60, paths.shape[0])
    for i in range(sample_n):
        fig_paths.add_trace(go.Scatter(y=paths[i], mode="lines", showlegend=False, opacity=0.35))

    fig_paths.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Months",
        yaxis_title="Balance (real terms)",
        height=320
    )

    # ----- Histogram + median/goal lines -----
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=final_values, nbinsx=60))

    # median line
    med = summary["median"]
    fig_hist.add_vline(x=med, line_dash="dash")

    # goal line if goal provided
    if goal and goal > 0:
        fig_hist.add_vline(x=goal, line_dash="dash")

    fig_hist.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Final balance (real terms)",
        yaxis_title="Count",
        height=320
    )

    stats_cards = dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div("Median", className="text-muted"),
            html.H4(money(summary["median"]))
        ]), className="mb-2"), width=6),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div("10th–90th percentile", className="text-muted"),
            html.H4(f"{money(summary['p10'])} – {money(summary['p90'])}")
        ]), className="mb-2"), width=6),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div("Goal probability", className="text-muted"),
            html.H4(f"{p_goal*100:.1f}%")
        ]), className="mb-2"), width=6),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div("Assumptions", className="text-muted"),
            html.Small(f"Return {params['r']*100:.0f}%, Vol {params['vol']*100:.0f}%, Inflation 2%")
        ]), className="mb-2"), width=6),
    ])

    return fig_paths, fig_hist, stats_cards

if __name__ == "__main__":
    app.run(debug=True)
