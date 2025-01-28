import mysql.connector

HOST = "prelim-program-database-do-user-18860734-0.f.db.ondigitalocean.com"
USER = "doadmin"
PASSWORD = "AVNS_M6ypXrCa1JjgD65mbBX"
DATABASE = "defaultdb"
TABLE_NAME = "claims"  # <-- change to your table name
PORT = 25060            # If needed, set your custom port here

def check_final_report_paragraph():
    conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = conn.cursor()
    
    # Query to select rows containing "No Final Report at this time."
    query = f"""
        SELECT id, Final_Report_Paragraph
        FROM {TABLE_NAME}
        WHERE Final_Report_Paragraph LIKE '%No Final Report at this time.%'
    """

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        matching_rows = []
        for row in results:
            row_id = row[0]
            paragraph = row[1]
            
            # Check if there is text BEFORE "No Final Report at this time."
            phrase = "No Final Report at this time."
            index_of_phrase = paragraph.find(phrase)
            
            # If the phrase is found and not at the very beginning (index 0),
            # that means there's text before the phrase.
            if index_of_phrase > 0:
                matching_rows.append((row_id, paragraph))

        # Print out the matching rows
        print("Rows that contain 'No Final Report at this time.' WITH text before it:")
        for r in matching_rows:
            print(f"ID: {r[0]}, Final_Report_Paragraph: {r[1]}")

    except mysql.connector.Error as err:
        print(f"[ERROR] {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_final_report_paragraph()
