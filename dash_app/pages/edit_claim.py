# pages/edit_claim.py
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
import pymysql
import requests  # Imported for fetching the DOCX file

from db import get_db_connection

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
            except Exception as e:
                print(f"Error fetching claim data for CID={cid}: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    # We store cid in a dcc.Store so we can access it in the callback
    store_cid = dcc.Store(id="cid-store", data=cid)

    return dmc.Stack(
        [
            store_cid,  # hidden, just holds the cid for the callback

            html.H3(f"Editing Claim: {cid}"),
            dmc.Text("Please fill out the fields below (data loaded from DB)."),

            # ========== Basic Fields in columns ==========
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Claim Number",
                        id="claim-number",
                        value=claim_data.get("claim_number", ""),
                        placeholder="Enter claim number",
                        style={"width": "45%"}
                    ),
                    dmc.TextInput(
                        label="Policyholder",
                        id="policyholder",
                        value=claim_data.get("Policyholder", ""),
                        placeholder="Enter policyholder name",
                        style={"width": "45%"}
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
                        style={"width": "45%"}
                    ),
                    dmc.TextInput(
                        label="Date of Loss",
                        id="date-of-loss",
                        value=claim_data.get("Date_Of_Loss", ""),
                        placeholder="YYYY-MM-DD",
                        style={"width": "45%"}
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
                        style={"width": "45%"}
                    ),
                    dmc.TextInput(
                        label="Adjuster Name",
                        id="adjuster-name",
                        value=claim_data.get("Adjuster_Name", ""),
                        placeholder="e.g. John Doe",
                        style={"width": "45%"}
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
                        style={"width": "45%"}
                    ),
                    dmc.TextInput(
                        label="Claim Type",
                        id="claim-type",
                        value=claim_data.get("Claim_Type", ""),
                        placeholder="e.g. Building & Contents",
                        style={"width": "45%"}
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
                        style={"width": "45%"}
                    ),
                    dmc.TextInput(
                        label="Contact Information (Insured)",
                        id="contact-info-insured",
                        value=claim_data.get("Insured_Contact_Info", ""),
                        placeholder="Phone / Email",
                        style={"width": "45%"}
                    ),
                ],
                justify="space-between"
            ),

            # ========== Coverage Fields in columns ==========
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage A",
                        id="coverage-a",
                        value=claim_data.get("coverage_building", ""),
                        placeholder="Building Coverage",
                        style={"width": "45%"}
                    ),
                    dmc.TextInput(
                        label="Coverage B",
                        id="coverage-b",
                        value=claim_data.get("coverage_contents", ""),
                        placeholder="Contents Coverage",
                        style={"width": "45%"}
                    ),
                ],
                justify="space-between",
                style={"marginTop": "1rem"}
            ),
            dmc.Group(
                [
                    dmc.TextInput(
                        label="Coverage A Deductible",
                        id="coverage-a-deductible",
                        value=claim_data.get("Coverage_A_Deductible", ""),
                        style={"width": "45%"}
                    ),
                    dmc.TextInput(
                        label="Coverage B Deductible",
                        id="coverage-b-deductible",
                        value=claim_data.get("Coverage_B_Deductible", ""),
                        style={"width": "45%"}
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
                        style={"width": "45%"}
                    ),
                    dmc.TextInput(
                        label="Coverage A Advance",
                        id="coverage-a-advance",
                        value=claim_data.get("Coverage_A_Advance", ""),
                        style={"width": "45%"}
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
                        style={"width": "30%"}
                    ),
                    dmc.TextInput(
                        label="Claim Contact Date",
                        id="claim-contact-date",
                        value=claim_data.get("Claim_Contact_Date", ""),
                        placeholder="YYYY-MM-DD",
                        style={"width": "30%"}
                    ),
                    dmc.TextInput(
                        label="Claim Inspection Date",
                        id="claim-inspection-date",
                        value=claim_data.get("Claim_Inspection_Date", ""),
                        placeholder="YYYY-MM-DD",
                        style={"width": "30%"}
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

            # ========== Save Button & Confirmation ==========
            dmc.Group(
                [
                    dmc.Button("Save Changes", id="save-button", color="blue"),
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
    },
)

        ],
        # Removed gap or spacing usage entirely
        style={"padding": "20px"},
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
    ],
    prevent_initial_call=True
)
def save_claim(
    n_clicks, cid,
    # Existing
    claim_number, policyholder, loss_address, date_of_loss, insurer, adjuster_name,
    policy_number, claim_type, contact_info_adjuster, contact_info_insured,
    coverage_a, coverage_a_deductible, coverage_a_reserve, coverage_a_advance,
    coverage_b, coverage_b_deductible, current_claim_status_par,
    # New
    claim_assigned_date, claim_contact_date, claim_inspection_date,
    preliminary_report_par, insured_communication_paragraph, claim_reserve_paragraph,
    insured_concern_paragraph, adjuster_response_paragraph, supporting_doc_paragraph,
    next_steps_paragraph, final_report_paragraph, claim_summary_par
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
            Claim_Type = %s,
            Adjuster_Contact_Info = %s,
            Insured_Contact_Info = %s,
            coverage_building = %s,
            Coverage_A_Deductible = %s,
            Coverage_A_Reserve = %s,
            Coverage_A_Advance = %s,
            coverage_contents = %s,
            Coverage_B_Deductible = %s,
            Current_Claim_Status_Par = %s,

            -- New fields
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
            Claim_Summary_Par = %s

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

            # WHERE
            claim_id
        ))
        conn.commit()
        msg = "Changes saved successfully!"
    except Exception as e:
        conn.rollback()
        msg = f"Error saving changes: {e}"
    finally:
        cursor.close()
        conn.close()

    return msg

@callback(
    Output("download-docx", "data"),
    Output("download-notification", "children"),
    Output("download-notification", "color"),
    Input("download-docx-button", "n_clicks"),
    State("cid-store", "data"),
    prevent_initial_call=True,
)
def download_docx(n_clicks, claim_number):
    if n_clicks is None or n_clicks == 0:
        return dash.no_update, dash.no_update, dash.no_update

    if not claim_number:
        return dash.no_update, "Invalid Claim ID.", "red"

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Fetch the report_spaces_link for the given cid
        sql = "SELECT report_spaces_link FROM claims WHERE id = %s"
        cursor.execute(sql, (claim_number,))
        result = cursor.fetchone()

        if not result or not result.get("report_spaces_link"):
            return dash.no_update, "Report link not found.", "red"

        report_link = result["report_spaces_link"]

        # Fetch the DOCX file from the report_link
        response = requests.get(report_link)
        if response.status_code != 200:
            return dash.no_update, "Failed to download the report.", "red"

        # Generate a filename for the downloaded file
        filename = f"Claim_{claim_number}_Report.docx"

        # Return the file and success notification
        return dcc.send_bytes(response.content, filename=filename), "Report downloaded successfully.", "green"

    except Exception as e:
        print(f"Error in download_docx callback: {e}")
        return dash.no_update, "An error occurred while downloading the report.", "red"

    finally:
        cursor.close()
        conn.close()
