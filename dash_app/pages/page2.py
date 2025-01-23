import dash
from dash import html

dash.register_page(__name__, path="/page2")

layout = html.Div(
    [html.H3("Page 2"), html.P("This is page 2 content.")]
)
