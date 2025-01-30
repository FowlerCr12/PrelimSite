import mysql.connector

HOST = "prelim-program-database-do-user-18860734-0.f.db.ondigitalocean.com"
USER = "doadmin"
PASSWORD = "AVNS_M6ypXrCa1JjgD65mbBX"
DATABASE = "defaultdb"
TABLE_NAME = "users"  # Changed to users table
PORT = 25060

def add_name_columns():
    conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = conn.cursor()

    try:
        # Add first_name and last_name columns
        alter_query = f"""
            ALTER TABLE {TABLE_NAME}
            ADD COLUMN first_name VARCHAR(50),
            ADD COLUMN last_name VARCHAR(50)
        """
        cursor.execute(alter_query)
        conn.commit()
        print("Successfully added first_name and last_name columns to users table")

    except mysql.connector.Error as err:
        print(f"[ERROR] {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_name_columns()
