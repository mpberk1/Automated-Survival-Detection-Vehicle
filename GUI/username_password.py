import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
import os
import subprocess

import sys
from pathlib import Path

#Dynamically get file paths
current_file = Path(__file__) # Path to this file
project_root = current_file.parent.parent # Path to Automated-Survival-Detection-Vehicle
sys.path.insert(0, str(project_root))

# functions from DatabaseManager.py
import DatabaseManager
from DatabaseManager.DatabaseManager import verify_user, insert_user

# Handle the login process
def login():
    username = usernameField.get()
    password = passwordField.get()

    if username and password:
        # Connect to the database
        try:
            conn = sqlite3.connect(project_root/"DatabaseManager/users.db")
            # insert_user(conn, "Admin", "pass")
            if verify_user(conn, username, password):
                result_label.config(text="Login successful!", foreground="green")
                root
                subprocess.Popen(['python3', project_root/"GUI/main_window.py"])
            else:
                result_label.config(text="Invalid username or password.", foreground="red")
        except sqlite3.Error as e:
            result_label.config(text="Database error.", foreground="red")
            print(f"Database error: {e}")
        finally:
            conn.close()
    else:
        result_label.config(text="Please enter both username and password.", foreground="red")

# GUI setup
root = Tk()
root.title('AGV-HSD Login')
root.geometry('300x200+150+150')
root.resizable(False, False)

frame = ttk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor=CENTER)

usernameField = ttk.Entry(frame, width=25)
usernameField.grid(row=0, column=0, padx=10, pady=5)
usernameField.insert(0, 'Username')

passwordField = ttk.Entry(frame, width=25)
passwordField.grid(row=1, column=0, padx=10, pady=5)
passwordField.insert(0, 'Password')

result_label = ttk.Label(frame, text="", width=25)
result_label.grid(row=3, column=0, padx=10, pady=5)

# Placeholder management
def typeUsername(event):
    if usernameField.get() == 'Username':
        usernameField.delete(0, END)

def typePassword(event):
    if passwordField.get() == 'Password':
        passwordField.delete(0, END)
        passwordField.config(show='*')

def resetPlaceholder(event):
    if usernameField.get() == '':
        usernameField.insert(0, 'Username')
    if passwordField.get() == '':
        passwordField.insert(0, 'Password')
        passwordField.config(show='')

usernameField.bind('<FocusIn>', typeUsername)
passwordField.bind('<FocusIn>', typePassword)
usernameField.bind('<FocusOut>', resetPlaceholder)
passwordField.bind('<FocusOut>', resetPlaceholder)

loginButton = ttk.Button(frame, text='Login', command=login)
loginButton.grid(row=2, column=0, columnspan=1, padx=10, pady=10)
root.bind('<Return>', lambda event: login())

root.mainloop()
