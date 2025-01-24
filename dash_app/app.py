import os
import json
from flask import Flask, request, jsonify
import dash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import Dash, _dash_renderer, Input, Output, State, callback, page_container
try:
    from dash import dcc
except ImportError:
    import dash_core_components as dcc

# =============== 1) CREATE THE FLASK SERVER ===============
server = Flask(__name__)

# =============== 2) CREATE THE DASH APP, ATTACHING THE SERVER ===============
_dash_renderer._set_react_version("18.2.0")

app = Dash(
    __name__,
    server=server,       # <-- We attach the Flask server here
    use_pages=True,      # If you want multi-page Dash
    external_stylesheets=dmc.styles.ALL,
)

# Example function for DB connection (fake example!)
def get_db_connection():
    # In real code, connect to MySQL or something
    # This is just a stub to avoid errors:
    return None

def get_icon(icon):
    return DashIconify(icon=icon, height=16)

navlinks_refresh = dmc.Stack(
    [
        dmc.NavLink(
            label="Home",
            leftSection=get_icon("bi:house-door-fill"),
            href="/",
            refresh=True,
            variant="subtle",
        ),
        dmc.NavLink(
            label="Need Review",
            leftSection=get_icon("tabler:gauge"),
            href="/page1",
            refresh=True,
            variant="subtle",
        ),
        dmc.NavLink(
            label="Approved Files",
            leftSection=get_icon("tabler:gauge"),
            href="/page2",
            refresh=True,
            variant="subtle",
        ),
        dmc.NavLink(
            label="Stats Dashboard",
            leftSection=get_icon("tabler:gauge"),
            href="/page3",
            refresh=True,
            variant="subtle",
        ),
    ],
    gap="sm",
)

navbar = dmc.AppShellNavbar(
    id="navbar",
    p="md",
    children=[
        dmc.Title("Nav Bar", order=4, mb="md"),
        navlinks_refresh,
    ],
    style={"backgroundColor": "#f1f3f5"}
)

header = dmc.AppShellHeader(
    dmc.Group(
        [
            dmc.Burger(id="burger", size="sm", hiddenFrom="sm", opened=False),
            dmc.Title("Status Report Program", c="blue"),
        ],
        h="100%",
        px="md",
    )
)

layout = dmc.AppShell(
    children=[
        header,
        navbar,
        dmc.AppShellMain(page_container),  # dash.page_container if use_pages=True
    ],
    header={"height": 60},
    padding="md",
    navbar={
        "width": 250,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
    },
    id="appshell",
)

app.layout = dmc.MantineProvider(layout)

# =============== 3) DASH CALLBACKS ===============
@callback(
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    State("appshell", "navbar"),
)
def navbar_is_open(opened, navbar):
    # Collapses the navbar on mobile if the burger is closed
    navbar["collapsed"] = {"mobile": not opened}
    return navbar

# =============== 4) FLASK ROUTE ON THE UNDERLYING "server" ===============
@server.route("/api/claim/<claim_number>", methods=["GET"])
def get_claim(claim_number):
    conn = get_db_connection()
    if not conn:
        # Just an example "fake" response if no real DB
        return jsonify({"error": "No DB connection stubbed"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT extracted_json FROM claims WHERE claim_number=%s", (claim_number,))
            row = cur.fetchone()
        if not row:
            return jsonify({"error": "Claim not found"}), 404
        return jsonify({"extracted_json": json.loads(row["extracted_json"])}), 200
    finally:
        conn.close()


# =============== 5) RUN THE DASH SERVER ===============
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
