# pages/page1.py
import dash
from dash import html, dash_table, callback, Output, Input, dcc
import dash_mantine_components as dmc
import pymysql
import os
from db import get_db_connection  # or however you import your helper

dash.register_page(__name__, path="/page1")

columns = [
    {"name": "CID",       "id": "claim_number"},
    {"name": "Insurer", "id": "Insurer"},
    {"name": "Review Status",     "id": "Review_Status"},
    {
        "name": "Download / Edit",
        "id": "View / Edit",
        "presentation": "markdown"  # interpret as clickable markdown link
    },
]

layout = html.Div(
    [
        html.H3("Claims Table"),
        dcc.Interval(id="refresh-claims-interval", interval=10*1000, n_intervals=0),  
        # ^ optional: triggers reloading data every 10s

        dash_table.DataTable(
            id="claims-table",
            columns=columns,
            data=[],  # We will fill this via callback
            page_size=15,
            style_cell={"whiteSpace": "pre-wrap", "padding": "8px"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"},
        ),
    ],
    style={"padding": "20px"},
    title=("CNC Report Generator")
)

@callback(
    Output("claims-table", "data"),
    Input("refresh-claims-interval", "n_intervals"),  # or a button click, etc.
)
def load_claims_data(n):
    """
    On page load (or on an interval), fetch claims from the DB and return them
    as a list of dicts for the Dash DataTable.
    """
    conn = None
    cursor = None
    rows_with_links = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # Ensure rows are returned as dicts

        # Example query fetching id, claim_number, and Insurer columns
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
        claims = cursor.fetchall()  # Fetch rows as a list of dicts

        # Add "View / Edit" links
        for row in claims:
            cid = row["id"]
            row["View / Edit"] = f"[Edit](/edit/{cid})"
            rows_with_links.append(row)

    except pymysql.Error as e:
        print("DB error:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return rows_with_links

