import sqlite3
import os

# Define the database file name
DB_NAME = 'app.db'

def init_db():
    """Initializes the SQLite database with necessary tables and initial items (recipes)."""
    # Check if the database file already exists
    if os.path.exists(DB_NAME):
        print(f"{DB_NAME} already exists. Skipping initialization.")
        return

    try:
        # Connect to the SQLite database (creates the file if it doesn't exist)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # 1. Create the 'items' table
        cursor.execute('''
            CREATE TABLE items (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL
            )
        ''')
        print("Table 'items' created successfully.")

        # 2. Create the 'likes' table
        # This table tracks which unique user (user_id) liked which item (item_id).
        # The combination of (user_id, item_id) is the primary key to enforce the 
        # one-like-per-user rule for a specific item.
        cursor.execute('''
            CREATE TABLE likes (
                user_id TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, item_id),
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        ''')
        print("Table 'likes' created successfully.")

        # Insert two distinct content items (recipes)
        cursor.execute("INSERT INTO items (id, title) VALUES (?, ?)", 
                       (1, "Spicy Thai Green Curry (Recipe 1)"))
        cursor.execute("INSERT INTO items (id, title) VALUES (?, ?)", 
                       (2, "Classic Chocolate Chip Cookies (Recipe 2)"))
        conn.commit()
        print("Initial content items (recipes) inserted.")

    except sqlite3.Error as e:
        print(f"An error occurred during database initialization: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()
