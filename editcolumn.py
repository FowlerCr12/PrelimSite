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

    # Change to DESCRIBE command
    describe_sql = f"DESCRIBE {TABLE_NAME};"

    try:
        cursor.execute(describe_sql)
        columns = cursor.fetchall()
        for column in columns:
            print(column)  # This will print each column's details
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    clear_table_rows()
