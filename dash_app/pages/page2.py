# pages/page1.py
import dash
from dash import html, dash_table, callback, Output, Input, dcc
import dash_mantine_components as dmc
import pymysql
import os
from db import get_db_connection  # or however you import your helper

dash.register_page(__name__, path="/registerUser")

layout = html.Div(
    [
        html.H3("Register New User"),
        dmc.Container(
            [
                dmc.TextInput(label="Email"),
                dmc.TextInput(label="Password"),
                dmc.TextInput(label="First Name"),
                dmc.TextInput(label="Last Name"),
                dmc.Button("Register", variant="filled", color="blue"),
            ]
        )
    ]
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
