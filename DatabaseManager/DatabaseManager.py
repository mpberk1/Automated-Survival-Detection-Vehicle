import sqlite3
import bcrypt

# Insert user with hashed password
def insert_user(conn, username, password):
    try:
        # Hash the plaintext password securely
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        sql_insert_user = '''INSERT INTO users (username, password)
                             VALUES (?, ?)'''
        conn.execute(sql_insert_user, (username, hashed_password))
        conn.commit()
        print(f"User '{username}' added successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")

# Verify user password
def verify_user(conn, username, password):
    try:
        sql_select_user = '''SELECT password FROM users WHERE username = ?'''
        cursor = conn.execute(sql_select_user, (username,))
        row = cursor.fetchone()
        
        if row:
            stored_password = row[0]
            # Compare the provided password with the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                return True
            else:
                return False
        else:
            return False
    except sqlite3.Error as e:
        print(f"Error verifying user: {e}")
        return False
