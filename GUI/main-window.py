from tkinter import *
from tkinter import ttk

#main window
root = Tk()
root.title('AGV-HSD')

#tab frame in root window
notebook = ttk.Notebook(root)
notebook.pack()

#create tabs
updatesTab = ttk.Frame(notebook)
trackingTab = ttk.Frame(notebook)
survivorTab = ttk.Frame(notebook)

#add tabs to notebook
notebook.add(updatesTab, text = 'AGV Status Updates')
notebook.add(trackingTab, text = 'Real-Time AGV Tracking')
notebook.add(survivorTab, text = 'Real-Time Survivor Detection Status')

#for AGV Status Updates Tab
updatesFrame = ttk.Frame(updatesTab)
updatesFrame.grid()

heartbeatLabel = ttk.Label(updatesFrame, text = 'Heartbeat Data').grid(row = 0, column = 0)
vocalLabel = ttk.Label(updatesFrame, text = 'Vocal Response Data').grid(row = 0, column = 1)
bodytempLabel = ttk.Label(updatesFrame, text = 'Body Temp Data').grid(row = 1, column = 0)
movementLabel = ttk.Label(updatesFrame, text = 'Manual AGV Control').grid(row = 1, column = 1)
armLabel = ttk.Label(updatesFrame, text = 'Mechanical Arm Control').grid(row = 0, column = 2, rowspan = 2)

#for Real-Time AGV Tracking Tab
canvas = Canvas(trackingTab)
canvas.grid()
canvas.config(width = 700, height = 500)
centerLine = canvas.create_line(350, 50, 350, 450, fill = 'white', width =2)


