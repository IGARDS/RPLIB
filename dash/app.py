import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# the style arguments for the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position to the right of the sidebar
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("RP Lib", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Search datasets", href="/", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
                dbc.NavLink("Page 3", href="/page-3", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# components for 'Search datasets' page
df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/solar.csv")

dataset = dash_table.DataTable(
    id="table",
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict("records"),
    is_focused=True,
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold',
        "border": "1px solid white",
    },
    filter_action='native',
    style_data={
        "backgroundColor": '#E3F2FD',
        "border-bottom": "1px solid #90CAF9",
        "border-top": "1px solid #90CAF9",
        "border-left": "1px solid #E3F2FD",
        "border-right": "1px solid #E3F2FD"},
    style_data_conditional=[
        {
            "if": {"state": "selected"},
            "backgroundColor": '#E3F2FD',
            "border-bottom": "1px solid #90CAF9",
            "border-top": "1px solid #90CAF9",
            "border-left": "1px solid #E3F2FD",
            "border-right": "1px solid #E3F2FD",
        }
    ]
)

page_1 = html.Div([
    html.H1("Search datasets"),
    html.P("Try searching for a dataset with filtered fields. Select a row to navigate to the raw dataset."),
    dataset,
    html.Div(id="output")
])


@app.callback(
    Output("output", "children"),
    Input("table", "active_cell"),
    State("table", "derived_viewport_data"),
)
def cell_clicked(cell, data):
    if cell:
        selected = data[cell["row"]]['State']
        return html.A(
            "View {}.json on GitHub".format(selected), href='https://github.com/someRPLibfolder/{}.json'.format(selected)
        )
    else:
        return dash.no_update


# components for all pages
content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return page_1
    elif pathname == "/page-2":
        return html.P("This is the content of page 2")
    elif pathname == "/page-3":
        return html.P("This is the content of page 3")
    # if the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(
                "The pathname {pathname} was not recognised...".format(pathname))
        ]
    )


if __name__ == "__main__":
    app.run_server(port=8888)
