import mysql.connector

# Adjust these to match your actual DB credentials
DB_HOST = "prelim-program-database-do-user-18860734-0.f.db.ondigitalocean.com"
DB_PORT = 25060  # or your actual port
DB_USER = "doadmin"
DB_PASSWORD = "AVNS_M6ypXrCa1JjgD65mbBX"
DB_NAME = "defaultdb"

def set_default_review_status():
    """
    Connects to MySQL and sets the default value of Review_Status in 'claims' to 'In Review'.
    """
    # 1) Connect
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    try:
        # 2) Run ALTER TABLE
        sql = """
        ALTER TABLE claims
        ALTER COLUMN Review_Status SET DEFAULT 'In Review'
        """
        # Depending on MySQL version, some might prefer:
        #   ALTER TABLE claims
        #   MODIFY Review_Status VARCHAR(255) DEFAULT 'In Review'
        # If "ALTER COLUMN ... SET DEFAULT" is unsupported, try "MODIFY":
        #
        # sql = "ALTER TABLE claims MODIFY Review_Status VARCHAR(255) DEFAULT 'In Review'"

        cursor.execute(sql)
        conn.commit()
        print("Default value for Review_Status set to 'In Review' successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error setting default value: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    set_default_review_status()
