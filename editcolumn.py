import mysql.connector

HOST = "prelim-program-database-do-user-18860734-0.f.db.ondigitalocean.com"
USER = "doadmin"
PASSWORD = "AVNS_M6ypXrCa1JjgD65mbBX"
DATABASE = "defaultdb"
TABLE_NAME = "claims"  # <-- change to your table name
PORT = 25060            # If needed, set your custom port here

def add_new_columns():
    conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = conn.cursor()

    # Add new columns for RCV Loss values
    alter_statements = [
        "ALTER TABLE claims ADD COLUMN DetachedGarage_Insured_Damage_RCV_Loss DECIMAL(10,2)",
        "ALTER TABLE claims ADD COLUMN DwellingUnit_Insured_Damage_RCV_Loss DECIMAL(10,2)",
        "ALTER TABLE claims ADD COLUMN Improvements_Insured_Damage_RCV_Loss DECIMAL(10,2)",
        "ALTER TABLE claims ADD COLUMN Contents_Insured_Damage_RCV_Loss DECIMAL(10,2)"
    ]

    try:
        for statement in alter_statements:
            try:
                cursor.execute(statement)
                conn.commit()
                print(f"Successfully executed: {statement}")
            except mysql.connector.Error as err:
                if err.errno == 1060:  # Duplicate column error
                    print(f"Column already exists, skipping: {statement}")
                else:
                    print(f"Error executing {statement}: {err}")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_new_columns()
