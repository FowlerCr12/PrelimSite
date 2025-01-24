# pip install docxtpl
from docxtpl import DocxTemplate

@app.route("/generate_claim_docx/<claim_number>", methods=["GET"])
def generate_claim_docx_tpl(claim_number):
    # 1) Fetch row
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM claims WHERE claim_number = %s", (claim_number,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return jsonify({"error": "Claim not found"}), 404

    # 2) docxtpl usage
    doc = DocxTemplate("/opt/PrelimSite/template.docx")

    # The docxtpl placeholders look like {{ Policyholder }} in the Word file
    context = {
        "Policyholder": row["Policyholder"],
        "Date_Of_Loss": row["Date_Of_Loss"],
        # ...
    }

    doc.render(context)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    filename = f"Claim_{claim_number}_Report.docx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
