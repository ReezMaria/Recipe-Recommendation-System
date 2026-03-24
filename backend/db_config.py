import oracledb

# Database connection setup
def get_connection():
    try:
        connection = oracledb.connect(
            user="system",               # change this
            password="livrset23!",    # change this
            dsn="localhost/XE"
        )
        return connection
    except Exception as e:
        print("Database connection error:", e)
        return None
