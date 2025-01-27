# pages/edit_claim.py
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
import pymysql
import requests  # Imported for fetching the DOCX file
from db import get_db_connection
import time
from io import BytesIO
import re
from docx import Document
from dotenv import load_dotenv
import json
from dash_iconify import DashIconify
import boto3
from botocore.config import Config
import os
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv('/opt/PrelimSite/.env')

dash.register_page(__name__, path_template="/edit/<cid>")

def layout(cid=None, **other_kwargs):
    """
    This layout function receives `cid` from the URL, queries the DB for that record,
    and populates the form fields with existing data.
    """

    # Initialize empty dict; if CID is valid, we'll overwrite with DB data
    claim_data = {}

    # Convert cid to int if needed, then query the DB
    if cid is not None:
        try:
            claim_id = int(cid)
        except ValueError:
            claim_id = None

        if claim_id:
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                sql = "SELECT * FROM claims WHERE id = %s"
                cursor.execute(sql, (claim_id,))
                row = cursor.fetchone()
                if row:
                    claim_data = row
                    print("DEBUG: Coverage Values from DB:")
                    print(f"Coverage A Deductible: {row.get('Coverage_A_Deductible')}")
                    print(f"Coverage A Reserve: {row.get('Coverage_A_Reserve')}")
                    print(f"Coverage A Advance: {row.get('Coverage_A_Advance')}")
                    print(f"Coverage B Deductible: {row.get('Coverage_B_Deductible')}")
                    print(f"Coverage B Reserve: {row.get('Coverage_B_Reserve')}")
                    print(f"Coverage B Advance: {row.get('Coverage_B_Advance')}")
            except Exception as e:
                print(f"Error fetching claim data for CID={cid}: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    # We store cid in a dcc.Store so we can access it in the callback
    store_cid = dcc.Store(id="cid-store", data=cid)

    # Parse JSON output from the correct column name
    json_data = {}
    try:
        if claim_data.get('extracted_json'):  # Changed from json_output to extracted_json
            json_data = json.loads(claim_data['extracted_json'])
    except json.JSONDecodeError:
        print("Error decoding JSON")

    # Create a mapping between your form fields and JSON types
    field_type_mapping = {
        "coverage-a-reserve": "Coverage-A-Building_Reserve",
        "coverage-a": "Coverage-A-Building",
        "coverage-a-deductible": "Coverage-A-Building_Deductible",
        "coverage-a-advance": "Coverage-A-Building_Advance",
        "coverage-b": "Coverage-B-Contents",
        "coverage-b-reserve": "Coverage-B-Contents_Reserve",
        "coverage-b-deductible": "Coverage-B-Contents_Deductible",
        "coverage-b-advance": "Coverage-B-Contents_Advance",
        "policyholder": "Policyholder_Name",
        "claim-number": "Claim_Number",
        "date-of-loss": "Date_Of_Loss",
        "insurer": "Insurer",
        "adjuster-name": "Adjuster_Name",
        "policy-number": "Policy_Number",
        "claim-type": "Claim_Type",
        "contact-info-adjuster": "Adjuster_Contact_Info",
        "contact-info-insured": "Insured_Contact_Info",
        "loss-address": "Loss_Address",
        "claim-assigned-date": "Claim_Assigned_Date",
        "claim-contact-date": "Claim_Contact_Date",
        "claim-inspection-date": "Claim_Inspection_Date",
        # Add more mappings as needed
    }

    def get_confidence(field_id):
        # Get the corresponding JSON type for this field
        json_type = field_type_mapping.get(field_id)
        if not json_type:
            return .90  # Default confidence if no mapping exists
        
        if json_data and 'entities' in json_data:
            for entity in json_data['entities']:
                if entity.get('type') == json_type:
                    return entity.get('confidence', 1.0)
        return 1.0

    def get_style(field_id, base_style=None):
        base_style = base_style or {}
        
        # Map component IDs to database column names
        field_mapping = {
            "coverage-a": "coverage_building",
            "coverage-b": "coverage_contents",
            "coverage-a-deductible": "Coverage_A_Deductible",
            "coverage-b-deductible": "Coverage_B_Deductible",
            "coverage-a-reserve": "Coverage_A_Reserve",
            "coverage-b-reserve": "Coverage_B_Reserve",
            "coverage-a-advance": "Coverage_A_Advance",
            "coverage-b-advance": "Coverage_B_Advance",
            "policyholder": "Policyholder",
            "claim-number": "claim_number",
            "date-of-loss": "Date_Of_Loss",
            "insurer": "Insurer",
            "adjuster-name": "Adjuster_Name",
            "policy-number": "Policy_Number",
            "claim-type": "claim_type",
            "contact-info-adjuster": "Adjuster_Contact_Info",
            "contact-info-insured": "Insured_Contact_Info",
            "loss-address": "Loss_Address",
            "claim-assigned-date": "Claim_Assigned_Date",
            "claim-contact-date": "Claim_Contact_Date",
            "claim-inspection-date": "Claim_Inspection_Date"
        }
        
        # Get the correct database column name
        db_field = field_mapping.get(field_id, field_id)
        value = claim_data.get(db_field)  # Get the field value
        
        # Handle None values and strip whitespace if it's a string
        if value is None:
            value = ""
        elif isinstance(value, str):
            value = value.strip()
        
        confidence = get_confidence(field_id)
        
        print(f"DEBUG: Style for {field_id} (DB field: {db_field}) - value: {value} - confidence: {confidence}")
        
        if not value:  # Check if field is blank or only whitespace
            print(f"DEBUG: Applying yellow style to {field_id} (blank field)")
            base_style["backgroundColor"] = "#fff3e0"  # Light yellow
            base_style["borderColor"] = "#ffa726"      # Orange/yellow
        elif confidence < 0.96:
            print(f"DEBUG: Applying red style to {field_id}")
            base_style["backgroundColor"] = "#ffebee"  # Light red
            base_style["borderColor"] = "#ef5350"      # Red
        else:
            print(f"DEBUG: Applying green style to {field_id}")
            base_style["backgroundColor"] = "#e8f5e9"  # Light green
            base_style["borderColor"] = "#66bb6a"      # Green
            
        return base_style

    return dmc.Stack(
        [
            store_cid,  # hidden, just holds the cid for the callback

            # Create a Group to hold the heading, button, and tooltip
            dmc.Group(
                [
                    # Left side with heading and tooltip
                    dmc.Group(
                        [
                            html.H3(f"Editing Claim: {cid}", style={"margin": 0}),
                            dmc.Tooltip(
                                label=dmc.List(
                                    spacing="xs",
                                    size="sm",
                                    children=[
                                        dmc.ListItem(
                                            "Green: Verified data (confidence > 96%). Information is most likely correct.",
                                            icon=dmc.ThemeIcon(
                                                DashIconify(icon="radix-icons:check", width=16),
                                                radius="xl",
                                                color="green",
                                                size=24,
                                            ),
                                        ),
                                        dmc.ListItem(
                                            "Yellow: Empty field needs attention. May or may not need to be filled out.",
                                            icon=dmc.ThemeIcon(
                                                DashIconify(icon="radix-icons:question-mark", width=16),
                                                radius="xl",
                                                color="yellow",
                                                size=24,
                                            ),
                                        ),
                                        dmc.ListItem(
                                            "Red: Low confidence data. Program not confident in this information. (< 96%)",
                                            icon=dmc.ThemeIcon(
                                                DashIconify(icon="radix-icons:exclamation-triangle", width=16),
                                                radius="xl",
                                                color="red",
                                                size=24,
                                            ),
                                        ),
                                    ],
                                ),
                                multiline=True,
                                maw=300,
                                children=dmc.ThemeIcon(
                                    DashIconify(icon="radix-icons:question-mark", width=16),
                                    radius="xl",
                                    color="gray",
                                    size=24,
                                    style={"cursor": "help"}
                                ),
                            ),
                        ],
                        gap="xs",
                    ),
                    # Right side button - now with _blank target
                    html.A(
                        dmc.Button(
                            "View Binder PDF",
                            color="blue",
                            variant="filled",
                            leftSection=html.I(className="fas fa-file-pdf"),
                        ),
                        id="view-binder-link",
                        href="#",
                        target="_blank",  # Changed back to _blank to open in new window
                        rel="noopener noreferrer",  # Added for security best practices
                        style={"textDecoration": "none"}
                    ),
                ],
                justify="space-between",
                align="center",
            ),
            
            dmc.Text("Please fill out the fields below (data loaded from DB)."),

            # ========== Basic Fields in columns ==========
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Claim Number",
                        id="claim-number",
                        value=claim_data.get("claim_number", ""),
                        placeholder="Enter claim number",
                        style=get_style("claim-number", {"width": "45%"}),
                    ),
                    dmc.TextInput(
                        label="Policyholder",
                        id="policyholder",
                        value=claim_data.get("Policyholder", ""),
                        placeholder="Enter policyholder name",
                        style=get_style("policyholder", {"width": "45%"}),
                    ),
                ],
                justify="space-between",
                style={"marginTop": "1rem"}
            ),

            dmc.Group(
                [
                    dmc.TextInput(
                        label="Loss Address",
                        id="loss-address",
                        value=claim_data.get("Loss_Address", ""),
                        placeholder="Enter loss address",
                        style=get_style("loss-address", {"width": "45%"}),
                    ),
                    dmc.TextInput(
                        label="Date of Loss",
                        id="date-of-loss",
                        value=claim_data.get("Date_Of_Loss", ""),
                        placeholder="YYYY-MM-DD",
                        style=get_style("date-of-loss", {"width": "45%"}),
                    ),
                ],
                justify="space-between"
            ),

            dmc.Group(
                [
                    dmc.TextInput(
                        label="Insurer",
                        id="insurer",
                        value=claim_data.get("Insurer", ""),
                        placeholder="e.g. Acme Insurance",
                        style=get_style("insurer", {"width": "45%"}),
                    ),
                    dmc.TextInput(
                        label="Adjuster Name",
                        id="adjuster-name",
                        value=claim_data.get("Adjuster_Name", ""),
                        placeholder="e.g. John Doe",
                        style=get_style("adjuster-name", {"width": "45%"}),
                    ),
                ],
                justify="space-between"
            ),

            dmc.Group(
                [
                    dmc.TextInput(
                        label="Policy Number",
                        id="policy-number",
                        value=claim_data.get("Policy_Number", ""),
                        placeholder="Policy #",
                        style=get_style("policy-number", {"width": "45%"}),
                    ),
                    dmc.TextInput(
                        label="Claim Type",
                        id="claim-type",
                        value=claim_data.get("claim_type", ""),
                        placeholder="Building Only/Contents Only/Building and Contents",
                        style=get_style("claim-type", {"width": "45%"}),
                    ),
                ],
                justify="space-between"
            ),

            dmc.Group(
                [
                    dmc.TextInput(
                        label="Contact Information (Adjuster)",
                        id="contact-info-adjuster",
                        value=claim_data.get("Adjuster_Contact_Info", ""),
                        placeholder="Phone / Email",
                        style=get_style("contact-info-adjuster", {"width": "45%"}),
                    ),
                    dmc.TextInput(
                        label="Contact Information (Insured)",
                        id="contact-info-insured",
                        value=claim_data.get("Insured_Contact_Info", ""),
                        placeholder="Phone / Email",
                        style=get_style("contact-info-insured", {"width": "45%"}),
                    ),
                ],
                justify="space-between"
            ),

            # ========== Coverage Fields in columns ==========
            # Coverage A and its RCV Loss values
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage A",
                        id="coverage-a",
                        value=claim_data.get("coverage_building", ""),
                        placeholder="Building Coverage",
                        style=get_style("coverage-a")
                    ),
                ],
                justify="space-between",
                style={"marginTop": "1rem"}
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Dwelling Unit RCV Loss",
                        id="dwelling-unit-rcv-loss",
                        value=claim_data.get("DwellingUnit_Insured_Damage_RCV_Loss", ""),
                        placeholder="Enter RCV Loss amount",
                        style=get_style("dwelling-unit-rcv-loss")
                    ),
                    dmc.TextInput(
                        label="Detached Garage RCV Loss",
                        id="detached-garage-rcv-loss",
                        value=claim_data.get("DetachedGarage_Insured_Damage_RCV_Loss", ""),
                        placeholder="Enter RCV Loss amount",
                        style=get_style("detached-garage-rcv-loss")
                    ),
                ],
                justify="space-between"
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Improvements RCV Loss",
                        id="improvements-rcv-loss",
                        value=claim_data.get("Improvements_Insured_Damage_RCV_Loss", ""),
                        placeholder="Enter RCV Loss amount",
                        style=get_style("improvements-rcv-loss")
                    ),
                ],
                justify="space-between"
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage A Deductible",
                        id="coverage-a-deductible",
                        value=claim_data.get("Coverage_A_Deductible", ""),
                        style=get_style("coverage-a-deductible")
                    ),
                ],
                justify="space-between"
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage A Reserve",
                        id="coverage-a-reserve",
                        value=claim_data.get("Coverage_A_Reserve", ""),
                        style=get_style("coverage-a-reserve")
                    ),
                ],
                justify="space-between"
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage A Advance",
                        id="coverage-a-advance",
                        value=claim_data.get("Coverage_A_Advance", ""),
                        style=get_style("coverage-a-advance")
                    ),
                ],
                justify="space-between"
            ),

            # Coverage B and its RCV Loss value
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage B",
                        id="coverage-b",
                        value=claim_data.get("coverage_contents", ""),
                        placeholder="Contents Coverage",
                        style=get_style("coverage-b")
                    ),
                ],
                justify="space-between"
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Contents RCV Loss",
                        id="contents-rcv-loss",
                        value=claim_data.get("Contents_Insured_Damage_RCV_Loss", ""),
                        placeholder="Enter RCV Loss amount",
                        style=get_style("contents-rcv-loss")
                    ),
                ],
                justify="space-between"
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage B Deductible",
                        id="coverage-b-deductible",
                        value=claim_data.get("Coverage_B_Deductible", ""),
                        style=get_style("coverage-b-deductible")
                    ),
                ],
                justify="space-between"
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage B Reserve",
                        id="coverage-b-reserve",
                        value=claim_data.get("Coverage_B_Reserve", ""),
                        style=get_style("coverage-b-reserve")
                    ),
                ],
                justify="space-between"
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage B Advance",
                        id="coverage-b-advance",
                        value=claim_data.get("Coverage_B_Advance", ""),
                        style=get_style("coverage-b-advance")
                    ),
                ],
                justify="space-between"
            ),

            # ========== Paragraph Field (full width) ==========
            dmc.Textarea(
                label="Current Claim Status Paragraph",
                id="Current_Claim_Status_Par",
                value=claim_data.get("Current_Claim_Status_Par", ""),
                placeholder="Summarize the current claim status...",
                minRows=3,
                style={"marginTop": "1rem"}
            ),

            # ========== NEW FIELDS: Dates in columns ==========
            # Here we have 3 date fields, let's place them in a single row
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Claim Assigned Date",
                        id="claim-assigned-date",
                        value=claim_data.get("Claim_Assigned_Date", ""),
                        placeholder="YYYY-MM-DD",
                        style=get_style("claim-assigned-date", {"width": "30%"})
                    ),
                    dmc.TextInput(
                        label="Claim Contact Date",
                        id="claim-contact-date",
                        value=claim_data.get("Claim_Contact_Date", ""),
                        placeholder="YYYY-MM-DD",
                        style=get_style("claim-contact-date", {"width": "30%"})
                    ),
                    dmc.TextInput(
                        label="Claim Inspection Date",
                        id="claim-inspection-date",
                        value=claim_data.get("Claim_Inspection_Date", ""),
                        placeholder="YYYY-MM-DD",
                        style=get_style("claim-inspection-date", {"width": "30%"})
                    ),
                ],
                justify="space-between",
                style={"marginTop": "1rem"}
            ),

            # ========== Paragraph-type fields (full width) ==========
            dmc.Textarea(
                label="Preliminary Report Paragraph",
                id="preliminary-report-par",
                value=claim_data.get("Preliminary_Report_Par", ""),
                placeholder="Details for Preliminary Report...",
                minRows=3,
                style={"marginTop": "1rem"}
            ),
            dmc.Textarea(
                label="Insured Communication Paragraph",
                id="insured-communication-paragraph",
                value=claim_data.get("Insured_Communication_Paragraph", ""),
                placeholder="Details about communication with the insured...",
                minRows=3
            ),
            dmc.Textarea(
                label="Claim Reserve Paragraph",
                id="claim-reserve-paragraph",
                value=claim_data.get("Claim_Reserve_Paragraph", ""),
                placeholder="Details about the claim reserves...",
                minRows=3
            ),
            dmc.Textarea(
                label="Insured Concern Paragraph",
                id="insured-concern-paragraph",
                value=claim_data.get("Insured_Concern_Paragraph", ""),
                placeholder="Summarize any insured concerns...",
                minRows=3
            ),
            dmc.Textarea(
                label="Adjuster Response Paragraph",
                id="adjuster-response-paragraph",
                value=claim_data.get("Adjuster_Response_Paragraph", ""),
                placeholder="Adjuster's response or actions taken...",
                minRows=3
            ),
            dmc.Textarea(
                label="Supporting Documents Paragraph",
                id="supporting-doc-paragraph",
                value=claim_data.get("Supporting_Doc_Paragraph", ""),
                placeholder="Summary of supporting documents...",
                minRows=3
            ),
            dmc.Textarea(
                label="Next Steps Paragraph",
                id="next-steps-paragraph",
                value=claim_data.get("Next_Steps_Paragraph", ""),
                placeholder="Outline the next steps in the claim process...",
                minRows=3
            ),
            dmc.Textarea(
                label="Final Report Paragraph",
                id="final-report-paragraph",
                value=claim_data.get("Final_Report_Paragraph", ""),
                placeholder="Details of the final report...",
                minRows=3
            ),
            dmc.Textarea(
                label="Claim Summary Paragraph",
                id="claim-summary-par",
                value=claim_data.get("Claim_Summary_Par", ""),
                placeholder="A concise summary of the claim...",
                minRows=3
            ),
            dmc.Select(
            label="Review Status",
            id="review-status",
            value=claim_data.get("Review_Status", "In Review"),
            data=[
                {"label": "In Review",  "value": "In Review"},
                {"label": "Reviewed",   "value": "Reviewed"},
                
                {"label": "Needs Work", "value": "Needs Work"},
            ],
            style={"width": "45%"}
        ),

            # ========== Save Button & Confirmation ==========
            dmc.Group(
                [
                    dmc.Button("Save Changes", id="save-button", color="blue", variant="filled"),
                ],
                justify="flex-end",
                style={"marginTop": "1rem"}
            ),
            html.Div(
                id="save-confirmation",
                style={"color": "green", "marginTop": "1rem"}
            ),
            

            # ======= Download Report Button =======
            dmc.Button(
                "Download Report",
                id="download-docx-button",
                n_clicks=0,
                color="blue",
                variant="filled",
                fullWidth=True,
                mt="md",
            ),

            # ======= Download Component =======
            dcc.Download(id="download-docx"),

            # ======= Notification Container =======
            dmc.Notification(
                id="download-notification",
                title="Download Complete",
                message="Your file has been successfully downloaded.",
                color="green",
                autoClose=5000,
                action={
                    "label": "Close",
                    "onClick": "function() { return false; }"
                }
            ),

        ],
        # Removed gap or spacing usage entirely
        style={"padding": "20px"}
    )

@callback(
    Output("save-confirmation", "children"),
    Input("save-button", "n_clicks"),
    [
        State("cid-store", "data"),
        # Existing Fields
        State("claim-number", "value"),
        State("policyholder", "value"),
        State("loss-address", "value"),
        State("date-of-loss", "value"),
        State("insurer", "value"),
        State("adjuster-name", "value"),
        State("policy-number", "value"),
        State("claim-type", "value"),
        State("contact-info-adjuster", "value"),
        State("contact-info-insured", "value"),
        State("coverage-a", "value"),
        State("coverage-a-deductible", "value"),
        State("coverage-a-reserve", "value"),
        State("coverage-a-advance", "value"),
        State("coverage-b", "value"),
        State("coverage-b-deductible", "value"),
        State("coverage-b-reserve", "value"),
        State("coverage-b-advance", "value"),
        State("Current_Claim_Status_Par", "value"),
        # New Fields
        State("claim-assigned-date", "value"),
        State("claim-contact-date", "value"),
        State("claim-inspection-date", "value"),
        State("preliminary-report-par", "value"),
        State("insured-communication-paragraph", "value"),
        State("claim-reserve-paragraph", "value"),
        State("insured-concern-paragraph", "value"),
        State("adjuster-response-paragraph", "value"),
        State("supporting-doc-paragraph", "value"),
        State("next-steps-paragraph", "value"),
        State("final-report-paragraph", "value"),
        State("claim-summary-par", "value"),
        State("review-status", "value"),
        # Add new RCV Loss states
        State("dwelling-unit-rcv-loss", "value"),
        State("detached-garage-rcv-loss", "value"),
        State("improvements-rcv-loss", "value"),
        State("contents-rcv-loss", "value"),
    ],
    prevent_initial_call=True
)
def save_claim(
    n_clicks, cid,
    claim_number, policyholder, loss_address, date_of_loss, insurer, adjuster_name,
    policy_number, claim_type, contact_info_adjuster, contact_info_insured,
    coverage_a, coverage_a_deductible, coverage_a_reserve, coverage_a_advance,
    coverage_b, coverage_b_deductible, coverage_b_reserve, coverage_b_advance,
    current_claim_status_par,
    claim_assigned_date, claim_contact_date, claim_inspection_date,
    preliminary_report_par, insured_communication_paragraph, claim_reserve_paragraph,
    insured_concern_paragraph, adjuster_response_paragraph, supporting_doc_paragraph,
    next_steps_paragraph, final_report_paragraph, claim_summary_par, review_status,
    dwelling_unit_rcv_loss, detached_garage_rcv_loss,
    improvements_rcv_loss, contents_rcv_loss
):
    """
    When the user clicks 'Save Changes', update the database with the new values.
    """
    if not cid:
        return "No CID provided, cannot save."

    # Attempt to convert cid to int
    try:
        claim_id = int(cid)
    except ValueError:
        return "Invalid CID. Could not convert to int."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        UPDATE claims
        SET
            claim_number = %s,
            Policyholder = %s,
            Loss_Address = %s,
            Date_Of_Loss = %s,
            Insurer = %s,
            Adjuster_Name = %s,
            Policy_Number = %s,
            claim_type = %s,
            Adjuster_Contact_Info = %s,
            Insured_Contact_Info = %s,
            coverage_building = %s,
            Coverage_A_Deductible = %s,
            Coverage_A_Reserve = %s,
            Coverage_A_Advance = %s,
            coverage_contents = %s,
            Coverage_B_Deductible = %s,
            Coverage_B_Reserve = %s,
            Coverage_B_Advance = %s,
            Current_Claim_Status_Par = %s,
            Claim_Assigned_Date = %s,
            Claim_Contact_Date = %s,
            Claim_Inspection_Date = %s,
            Preliminary_Report_Par = %s,
            Insured_Communication_Paragraph = %s,
            Claim_Reserve_Paragraph = %s,
            Insured_Concern_Paragraph = %s,
            Adjuster_Response_Paragraph = %s,
            Supporting_Doc_Paragraph = %s,
            Next_Steps_Paragraph = %s,
            Final_Report_Paragraph = %s,
            Claim_Summary_Par = %s,
            DwellingUnit_Insured_Damage_RCV_Loss = %s,
            DetachedGarage_Insured_Damage_RCV_Loss = %s,
            Improvements_Insured_Damage_RCV_Loss = %s,
            Contents_Insured_Damage_RCV_Loss = %s,
            Review_Status = %s
        WHERE id = %s
        """

        cursor.execute(sql, (
            # Existing fields
            claim_number,
            policyholder,
            loss_address,
            date_of_loss,
            insurer,
            adjuster_name,
            policy_number,
            claim_type,
            contact_info_adjuster,
            contact_info_insured,
            coverage_a,
            coverage_a_deductible,
            coverage_a_reserve,
            coverage_a_advance,
            coverage_b,
            coverage_b_deductible,
            coverage_b_reserve,
            coverage_b_advance,
            current_claim_status_par,

            # New fields
            claim_assigned_date,
            claim_contact_date,
            claim_inspection_date,
            preliminary_report_par,
            insured_communication_paragraph,
            claim_reserve_paragraph,
            insured_concern_paragraph,
            adjuster_response_paragraph,
            supporting_doc_paragraph,
            next_steps_paragraph,
            final_report_paragraph,
            claim_summary_par,
            dwelling_unit_rcv_loss,
            detached_garage_rcv_loss,
            improvements_rcv_loss,
            contents_rcv_loss,
            review_status,

            # WHERE
            claim_id
        ))
        conn.commit()
        msg = "Changes saved successfully!"
        print("Changes saved successfully!")
    except Exception as e:
        conn.rollback()
        msg = f"Error saving changes: {e}"
    finally:
        cursor.close()
        conn.close()

    return msg

def paragraph_replace_text(paragraph, regex, replace_str):
    """
    Replaces matches for 'regex' with 'replace_str' across runs in a paragraph.
    """
    while True:
        text = paragraph.text
        match = regex.search(text)
        if not match:
            break

        runs = iter(paragraph.runs)
        start, end = match.start(), match.end()

        # Advance past runs that do not contain the start of the match
        for run in runs:
            run_len = len(run.text)
            if start < run_len:
                break
            start -= run_len
            end -= run_len

        run_text = run.text
        run_len = len(run_text)
        # Replace the part of the match in this run with the replacement text
        run.text = f"{run_text[:start]}{replace_str}{run_text[end:]}"
        end -= run_len

        # Remove the remainder of the matched text from subsequent runs
        for run in runs:
            if end <= 0:
                break
            run_text = run.text
            run_len = len(run_text)
            run.text = run_text[end:]
            end -= run_len


def replace_in_paragraphs(doc, replacements):
    """
    Iterates over all paragraphs and tables in the doc, performing regex replacements.
    """
    # Replace in normal paragraphs
    for paragraph in doc.paragraphs:
        for pattern, replace_str in replacements.items():
            regex = re.compile(pattern)
            paragraph_replace_text(paragraph, regex, replace_str)

    # Replace in tables as well
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for pattern, replace_str in replacements.items():
                        regex = re.compile(pattern)
                        paragraph_replace_text(paragraph, regex, replace_str)

@callback(
    Output("download-docx", "data"),
    Output("download-notification", "children"),
    Output("download-notification", "color"),
    Input("download-docx-button", "n_clicks"),
    State("cid-store", "data"),
    prevent_initial_call=True,
)
def download_docx(n_clicks, row_id):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update

    # Fetch row from DB
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM claims WHERE id = %s", (row_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return dash.no_update, "Claim not found!", "red"

    # Use claim_number for filename instead of row_id
    filename = f"Claim_{row['claim_number']}_Report.docx"
    
    # 2) Build a replacements dict for naive placeholders like {{Policyholder}}
    # In your Word template, you'd have placeholders literally like "{{Policyholder}}"
    replacements = {
        r"\{\{Policyholder\}\}": row.get("Policyholder", ""),
        r"\{\{DateOfLoss\}\}": row.get("Date_Of_Loss", ""),
        r"\{\{Insurer_Name\}\}": row.get("Insurer", ""),
        r"\{\{Coverage_A_Advance\}\}": row.get("Coverage_A_Advance", ""),
        r"\{\{Coverage_A_Reserve\}\}": row.get("Coverage_A_Reserve", ""),
        r"\{\{Coverage_A_Deductible\}\}": row.get("Coverage_A_Deductible", ""),
        r"\{\{coverage_building\}\}": row.get("coverage_building", ""),
        r"\{\{claim_type\}\}": row.get("claim_type", ""),
        r"\{\{Insured_Contact_Info\}\}": row.get("Insured_Contact_Info", ""),
        r"\{\{Adjuster_Contact_Info\}\}": row.get("Adjuster_Contact_Info", ""),
        r"\{\{Current_Claim_Status_Par\}\}": row.get("Current_Claim_Status_Par", ""),
        r"\{\{Claim_Assigned_Date\}\}": row.get("Claim_Assigned_Date", ""),
        r"\{\{Claim_Contact_Date\}\}": row.get("Claim_Contact_Date", ""),
        r"\{\{Claim_Inspection_Date\}\}": row.get("Claim_Inspection_Date", ""),
        r"\{\{Preliminary_Report_Par\}\}": row.get("Preliminary_Report_Par", ""),
        r"\{\{Insured_Communication_Paragraph\}\}": row.get("Insured_Communication_Paragraph", ""),
        r"\{\{Claim_Reserve_Paragraph\}\}": row.get("Claim_Reserve_Paragraph", ""),
        r"\{\{Insured_Concern_Paragraph\}\}": row.get("Insured_Concern_Paragraph", ""),
        r"\{\{Next_Steps_Paragraph\}\}": row.get("Next_Steps_Paragraph", ""),
        r"\{\{Final_Report_Paragraph\}\}": row.get("Final_Report_Paragraph", ""),
        r"\{\{Claim_Summary_Par\}\}": row.get("Claim_Summary_Par", ""),
        r"\{\{Supporting_Doc_Paragraph\}\}": row.get("Supporting_Doc_Paragraph", ""),
        r"\{\{Adjuster_Response_Paragraph\}\}": row.get("Adjuster_Response_Paragraph", ""),
        r"\{\{coverage_contents\}\}": row.get("coverage_contents", ""),
        r"\{\{Coverage_B_Deductible\}\}": row.get("Coverage_B_Deductible", ""),
        r"\{\{Coverage_B_Reserve\}\}": row.get("Coverage_B_Reserve", ""),
        r"\{\{Coverage_B_Advance\}\}": row.get("Coverage_B_Advance", ""),
        r"\{\{Adjuster_Name\}\}": row.get("Adjuster_Name", ""),
        r"\{\{Policy_Number\}\}": row.get("Policy_Number", ""),
        r"\{\{claim_number\}\}": row.get("claim_number", ""),
        r"\{\{loss_address\}\}": row.get("Loss_Address", ""),
        


        
        # ... add as many placeholders as you used in your .docx
        # e.g. r"\{\{Insurer\}\}": row.get("Insurer", "")
    }

    # 3) Load the Word .docx template from disk
    # Make sure you actually have this file, and your placeholders in the doc are e.g. "{{Policyholder}}"
    from docx import Document
    template_path = "/opt/PrelimSite/template.docx"
    doc = Document(template_path)

    # 4) Perform the naive placeholder replacements
    replace_in_paragraphs(doc, replacements)

    # (Optional) Sleep for debugging or demonstration
    time.sleep(2)

    # 5) Save to in-memory buffer
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    # 6) Return a dcc.Download object + success message
    return dcc.send_bytes(buffer.getvalue(), filename), "Report downloaded successfully.", "green"

@callback(
    Output("view-binder-link", "href"),
    Input("cid-store", "data"),
    prevent_initial_call=False
)
def update_binder_link(cid):
    print("\n" + "=" * 50)
    print(f"Callback triggered with cid: {cid}")
    
    if not cid:
        print("No CID provided")
        return "#"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print(f"Querying database for claim_number: {cid}")
        cursor.execute("SELECT binder_spaces_link FROM claims WHERE id = %s", (cid,))
        result = cursor.fetchone()
        
        print(f"Database result: {result}")
        
        if not result or not result['binder_spaces_link']:
            print("No binder link found in database")
            return "#"
            
        spaces_link = result['binder_spaces_link']
        print(f"Found spaces link: {spaces_link}")
        
        # Parse the Spaces URL
        parsed_url = urlparse(spaces_link)
        bucket_name = 'prelim-program-file-storage'
        key = parsed_url.path.lstrip('/')
        
        print(f"Parsed bucket: {bucket_name}, key: {key}")
        
        session = boto3.session.Session()
        client = session.client('s3',
            region_name='nyc3',
            endpoint_url='https://nyc3.digitaloceanspaces.com',
            aws_access_key_id=os.getenv('SPACES_KEY'),
            aws_secret_access_key=os.getenv('SPACES_SECRET')
        )
        
        # Generate presigned URL with ResponseContentDisposition
        url = client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ResponseContentType': 'application/pdf',
                'ResponseContentDisposition': 'inline'  # This tells the browser to display the PDF
            },
            ExpiresIn=3600
        )
        
        print(f"Generated presigned URL: {url}")
        return url
        
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return "#"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()