import mysql.connector

HOST = "prelim-program-database-do-user-18860734-0.f.db.ondigitalocean.com"
USER = "doadmin"
PASSWORD = "AVNS_M6ypXrCa1JjgD65mbBX"
DATABASE = "defaultdb"
TABLE_NAME = "claims"  # <-- change to your table name
PORT = 25060            # If needed, set your custom port here

def remove_no_final_report_text():
    conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = conn.cursor()

    # Step 1: Select rows where Final_Report_Paragraph contains the target phrase
    phrase = "No Final Report at this time."
    select_query = f"""
        SELECT id, Final_Report_Paragraph
        FROM {TABLE_NAME}
        WHERE Final_Report_Paragraph LIKE %s
    """

    try:
        cursor.execute(select_query, (f"%{phrase}%",))
        rows = cursor.fetchall()

        for row in rows:
            row_id = row[0]
            paragraph = row[1] or ""  # In case it's NULL, convert to empty string

            # Step 2: Check if the phrase occurs, and there's text before it
            index_of_phrase = paragraph.find(phrase)
            if index_of_phrase > 0:
                # Step 3: Remove just that substring from the paragraph
                new_paragraph = (
                    paragraph[:index_of_phrase] +
                    paragraph[index_of_phrase + len(phrase):]
                )

                # Optional: You may want to strip excess whitespace 
                new_paragraph = new_paragraph.strip()

                # Update the row in the database
                update_query = f"""
                    UPDATE {TABLE_NAME}
                    SET Final_Report_Paragraph = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (new_paragraph, row_id))
                print(f"Updated ID={row_id}:\n  Old: {paragraph}\n  New: {new_paragraph}\n")

        # Commit all updates
        conn.commit()

    except mysql.connector.Error as err:
        print(f"[ERROR] {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    remove_no_final_report_text()
