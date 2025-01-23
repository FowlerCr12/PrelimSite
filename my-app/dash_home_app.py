import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, Input, Output, State, callback

_dash_renderer._set_react_version("18.2.0")

app = Dash(__name__, external_stylesheets=dmc.styles.ALL)

logo = "https://cdn.prod.website-files.com/6127cf52b9d335ca60c65756/6193e8b279a934f3cbd246a4_CNC.svg"

layout = dmc.AppShell(
    [
        dmc.AppShellHeader(
            dmc.Group(
                [
                    dmc.Burger(id="burger", size="sm", hiddenFrom="sm", opened=False),
                    dmc.Image(src=logo, h=40),    # Use h=40 (not height=40)
                    dmc.Title("Prelim Reviewer", c="blue"),
                ],
                h="100%",
                px="md",
            )
        ),
        dmc.AppShellNavbar(
            id="navbar",
            children=["Navbar"] + [dmc.Skeleton(height=28, mt="sm", animate=False) for _ in range(15)],
            p="md",
        ),
        dmc.AppShellMain("Main"),
    ],
    header={"height": 60},
    padding="md",
    navbar={
        "width": 300,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
    },
    id="appshell",
)

app.layout = dmc.MantineProvider(layout)

@callback(
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    State("appshell", "navbar"),
)
def navbar_is_open(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened}
    return navbar

if __name__ == "__main__":
    app.run(debug=True, port=8050)
