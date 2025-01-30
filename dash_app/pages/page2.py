# pages/page1.py
import dash
from dash import html, dash_table, callback, Output, Input, dcc, State, no_update
import dash_mantine_components as dmc
import pymysql
import os
from dash_iconify import DashIconify
from db import get_db_connection  # or however you import your helper
import bcrypt
from dash.exceptions import PreventUpdate
import json

dash.register_page(__name__, path="/registerUser")

def get_icon(icon):
    return DashIconify(icon=icon, height=16)

def register_user(email, password, first_name, last_name):
    """Register a new user with hashed password"""
    try:
        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO users (email, password_hash, first_name, last_name)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (
            email,
            hashed_password,  # Store the hashed password, not the plain text
            first_name,
            last_name
        ))
        conn.commit()
        return True, "User registered successfully"
        
    except pymysql.Error as e:
        print("Database error:", e)
        return False, f"Database error occurred: {str(e)}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Add new callback outputs for notifications
@callback(
    [
        Output("register-status", "children"),
        Output("success-notification", "children"),
        Output("error-notification", "children"),
    ],
    [
        Input("register-button", "n_clicks"),
        State("email-input", "value"),
        State("password-input", "value"),
        State("firstname-input", "value"),
        State("lastname-input", "value"),
    ],
)
def handle_registration(n_clicks, email, password, first_name, last_name):
    if not n_clicks:  # Don't trigger on page load
        raise PreventUpdate
    
    if not all([email, password, first_name, last_name]):
        return no_update, no_update, dmc.Notification(
            title="Error",
            message="Please fill in all fields",
            color="red",
            action="show",
            autoClose=4000,
        )
    
    success, message = register_user(email, password, first_name, last_name)
    
    if success:
        return (
            message,
            dmc.Notification(
                title="Success",
                message="User registered successfully",
                color="green",
                action="show",
                autoClose=4000,
            ),
            no_update,
        )
    else:
        return (
            message,
            no_update,
            dmc.Notification(
                title="Error",
                message="Could not register user",
                color="red",
                action="show",
                autoClose=4000,
            ),
        )

layout = html.Div(
    [
        # Add notification containers
        html.Div(id="success-notification"),
        html.Div(id="error-notification"),
        
        html.H3("Register New User"),
        dmc.Container(
            [
                dmc.TextInput(
                    id="email-input",
                    label="Email",
                    placeholder="Enter email",
                    leftSection=get_icon("tabler:at"),
                    required=True,
                    radius="md",
                ),
                dmc.PasswordInput(
                    id="password-input",
                    label="Password",
                    placeholder="Enter password",
                    leftSection=get_icon("tabler:lock"),
                    required=True,
                    radius="md",
                ),
                dmc.TextInput(
                    id="firstname-input",
                    label="First Name",
                    placeholder="Enter first name",
                    leftSection=get_icon("tabler:user"),
                    required=True,
                    radius="md",
                ),
                dmc.TextInput(
                    id="lastname-input",
                    label="Last Name",
                    placeholder="Enter last name",
                    leftSection=get_icon("tabler:user"),
                    required=True,
                    radius="md",
                ),
                dmc.Button(
                    "Register",
                    id="register-button",
                    variant="filled",
                    color="blue",
                    mt="md",
                    radius="md"
                ),
                html.Div(id="register-status", style={"marginTop": "1rem"}),
            ]
        )
    ]
)

