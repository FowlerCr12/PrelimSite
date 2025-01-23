import dash
from dash import html

dash.register_page(__name__, path="/page3")

layout = html.Div(
    [html.H3("Page 3"), html.P("This is page 3 content.")]
)
