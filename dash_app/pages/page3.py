import dash
from dash import html

dash.register_page(__name__, path="/page3")

layout = html.Div(
    [html.H3("Page 3"), html.P("WIP PAGE 3 CONTENT")]
)
