import sqlite3


# Create the 'users' table if it does not exist
# Create users table
def create_table(conn):
    try:
        sql_create_table = '''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT NOT NULL UNIQUE,
                                password TEXT NOT NULL);'''
        conn.execute(sql_create_table)
        #print("Table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")


# Insert user with plaintext password
def insert_user(conn, username, password):
    try:
        # Directly store the plaintext password (insecure)
        create_table(conn)
        sql_insert_user = '''INSERT INTO users (username, password)
                             VALUES (?, ?)'''
        conn.execute(sql_insert_user, (username, password))
        conn.commit()
        print(f"User '{username}' added successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")

# Verify user password
def verify_user(conn, username, password):
    try:
        create_table(conn)
        sql_select_user = '''SELECT password FROM users WHERE username = ?'''
        cursor = conn.execute(sql_select_user, (username,))
        row = cursor.fetchone()
        
        if row:
            stored_password = row[0]
            # Compare the provided password with the stored plaintext password
            if password == stored_password:
                return True
            else:
                return False
        else:
            return False
    except sqlite3.Error as e:
        print(f"Error verifying user: {e}")
        return False
