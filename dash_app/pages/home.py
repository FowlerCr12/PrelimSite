import dash
from dash import html

dash.register_page(__name__, path="/")

layout = html.Div(
    [html.H3("Home"), html.P("WIP HOME PAGE")]
)
