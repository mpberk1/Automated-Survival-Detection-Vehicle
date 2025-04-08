import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Entry, Label, Button, Frame
import sqlite3
import subprocess
import sys
from pathlib import Path

# Path configuration
current_file = Path(__file__)
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from DatabaseManager.DatabaseManager import verify_user

# ------------------- Functions ------------------- #

def login():
    username = usernameField.get()
    password = passwordField.get()

    if username and password:
        try:
            conn = sqlite3.connect(project_root / "DatabaseManager/users.db")
            if verify_user(conn, username, password):
                result_label.config(text="Login successful!", foreground="green")
                root.destroy()
                subprocess.Popen(['python3', str(project_root / "GUI/main_window.py")])
            else:
                result_label.config(text="Invalid username or password.", foreground="#e30613")
        except sqlite3.Error as e:
            result_label.config(text="Database error.", foreground="#e30613")
            print(f"Database error: {e}")
        finally:
            conn.close()
    else:
        result_label.config(text="Please enter both username and password.", foreground="white")

# ------------------- UI Setup ------------------- #

root = ttkb.Window(themename="darkly")  # Choose from: darkly, flatly, cyborg, etc.
root.title("AGV-HSD Login")
root.geometry("400x300")
root.resizable(False, False)

frame = Frame(root, padding=30)
frame.place(relx=0.5, rely=0.5, anchor="center")

title_label = Label(frame, text="AGV-HSD Login", font=('Segoe UI', 14, 'bold'), bootstyle="info")
title_label.grid(row=0, column=0, pady=(0, 20))

usernameField = Entry(frame, width=30)
usernameField.grid(row=1, column=0, pady=5)
usernameField.insert(0, 'Username')

passwordField = Entry(frame, width=30)
passwordField.grid(row=2, column=0, pady=5)
passwordField.insert(0, 'Password')

# Placeholder behavior
def typeUsername(event):
    if usernameField.get() == 'Username':
        usernameField.delete(0, 'end')

def typePassword(event):
    if passwordField.get() == 'Password':
        passwordField.delete(0, 'end')
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

loginButton = Button(frame, text='Login', command=login, bootstyle="primary")
loginButton.grid(row=3, column=0, pady=20)

result_label = Label(frame, text="", anchor="center", font=('Segoe UI', 12))
result_label.grid(row=4, column=0, pady=5)

root.bind('<Return>', lambda event: login())

root.mainloop()
