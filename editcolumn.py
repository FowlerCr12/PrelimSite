import mysql.connector

HOST = "prelim-program-database-do-user-18860734-0.f.db.ondigitalocean.com"
USER = "doadmin"
PASSWORD = "AVNS_M6ypXrCa1JjgD65mbBX"
DATABASE = "defaultdb"
TABLE_NAME = "claims"  # <-- change to your table name
PORT = 25060            # If needed, set your custom port here

def clear_table_rows():
    conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = conn.cursor()

    # Truncate the table to remove all rows but keep the structure
    clear_sql = f"TRUNCATE TABLE {TABLE_NAME};"

    try:
        cursor.execute(clear_sql)
        conn.commit()
        print(f"[INFO] All rows in '{TABLE_NAME}' have been removed, columns remain intact.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    clear_table_rows()
