import tkinter as tk
from tkinter import *
from tkinter import ttk

root = Tk()
root.title('Login')
root.geometry('400x100+150+150')
root.resizable(False,False)

usernameField = ttk.Entry(root, width = 30)
usernameField.pack()
usernameField.insert(0,'Username')

passwordField = ttk.Entry(root, width = 30)
passwordField.pack()
passwordField.insert(0,'Password')

loginButton = ttk.Button(root, text = 'Login')
loginButton.pack()

def mainFrame():
    mainFrame = Toplevel(root)

loginButton.config(command = mainFrame)

root.mainloop()
