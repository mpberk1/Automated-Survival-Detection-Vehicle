import sqlite3
import bcrypt

# Connect to SQLite database (or create it if it doesn't exist)
def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

# Create users table
def create_table(conn):
    try:
        sql_create_table = '''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT NOT NULL UNIQUE,
                                password TEXT NOT NULL);'''
        conn.execute(sql_create_table)
        print("Table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

# Insert user with hashed password
def insert_user(conn, username, password):
    try:
        # Hash the password using bcrypt
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
            stored_hashed_password = row[0]
            # Verify the password against the stored hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                print("Login successful!")
            else:
                print("Incorrect password!")
        else:
            print("User not found!")
    except sqlite3.Error as e:
        print(f"Error verifying user: {e}")

# Main function
def main():
    db_file = 'users.db'
    
    # Create database connection
    conn = create_connection(db_file)
    
    # Create users table if it doesn't exist
    create_table(conn)
    
    # Insert new user
    username = input("Enter username: ")
    password = input("Enter password: ")
    insert_user(conn, username, password)
    
    # Optionally verify the user
    verify_username = input("Enter username to verify: ")
    verify_password = input("Enter password to verify: ")
    verify_user(conn, verify_username, verify_password)
    
    # Close connection
    conn.close()

if __name__ == '__main__':
    main()
