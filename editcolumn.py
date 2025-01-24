import mysql.connector

HOST = "prelim-program-database-do-user-18860734-0.f.db.ondigitalocean.com"
USER = "doadmin"
PASSWORD = "AVNS_M6ypXrCa1JjgD65mbBX"
DATABASE = "defaultdb"
TABLE_NAME = "claims"  # <-- change to your table name
PORT = 25060            # If needed, set your custom port here

def make_id_autoincrement():
    conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = conn.cursor()

    # Just change 'id' to be auto_increment.
    alter_sql = f"""
        UPDATE claims
        SET Review_Status = 'Processing'
        WHERE Review_Status IS 'In Review';
    """

    try:
        cursor.execute(alter_sql)
        conn.commit()
        print("[INFO] 'id' column is now AUTO_INCREMENT.")
    except Exception as e:
        print(f"[ERROR] {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    make_id_autoincrement()