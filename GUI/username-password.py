import tkinter as tk
from tkinter import *
from tkinter import ttk
import sqlite3
import bcrypt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'DatabaseManager'))

from DatabaseManager import create_connection, create_table, verify_user, insert_user

def login():
    username = usernameField.get()
    password = passwordField.get()
    
    if username and password:
        conn = create_connection('users.db')

        if verify_user(conn, username, password):
            result_label.config(text="Login successful!", foreground="green")
            print("It worked.")
        else:
            result_label.config(text="Invalid username or password.", foreground="red")
            print("It NOT worked.")
        conn.close()
    else:
        result_label.config(text="Please enter both username and password.", foreground="red")
        print("Wrong info.")

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

# Add the result label here to display messages
result_label = ttk.Label(frame, text="", width=25)
result_label.grid(row=3, column=0, padx=10, pady=5)

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

# Set the command for the login button to call the login function
loginButton = ttk.Button(frame, text='Login', command=login)
loginButton.grid(row=2, column=0, columnspan=1, padx=10, pady=10)

root.mainloop()
