# pages/page1.py
import dash
from dash import html, dash_table, callback, Output, Input, dcc
import dash_mantine_components as dmc
import pymysql
import os
from db import get_db_connection  # or however you import your helper

dash.register_page(__name__, path="/page1")

columns = [
    {"name": "CID",            "id": "claim_number",   "type": "text"},
    {"name": "Insurer",        "id": "Insurer",        "type": "text"},
    {"name": "Review Status",  "id": "Review_Status",  "type": "text"},
    {
        "name": "Download / Edit",
        "id": "View / Edit",
        "presentation": "markdown"
    },
]

layout = html.Div(
    [
        html.H3("Claims Table"),
        # Optional auto-refresh every 10s:
        dcc.Interval(id="refresh-claims-interval", interval=10*1000, n_intervals=0),

        dash_table.DataTable(
            id="claims-table",
            columns=columns,
            data=[],    # We'll fill this via callback
            page_size=15,
            style_cell={"whiteSpace": "pre-wrap", "padding": "8px"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"},

            # Enable built-in filter for each column
            filter_action="native",
            # Optionally enable built-in sorting
            sort_action="native",
            sort_mode="multi",
            # (Optional) Provide a placeholder for filter fields
            filter_options={"placeholder_text": "Filter..."},
        ),
    ],
    style={"padding": "20px"},
)

@callback(
    Output("claims-table", "data"),
    Input("refresh-claims-interval", "n_intervals"),  # or a button, if you prefer
)
def load_claims_data(n):
    """
    On page load (or on an interval), fetch claims from the DB
    and return them as a list of dicts for the Dash DataTable.
    """
    conn = None
    cursor = None
    rows_with_links = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = """
        SELECT 
            id, 
            claim_number, 
            Insurer,
            Review_Status
        FROM claims 
        ORDER BY id DESC
        """
        cursor.execute(sql)
        claims = cursor.fetchall()

        # Add "View / Edit" link as clickable markdown
        for row in claims:
            cid = row["id"]
            row["View / Edit"] = f"[Edit](/dash/edit/{cid})"
            rows_with_links.append(row)

    except pymysql.Error as e:
        print("DB error:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return rows_with_links
