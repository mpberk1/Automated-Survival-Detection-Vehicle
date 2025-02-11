
import tkinter as tk
from tkinter import *
from tkinter import ttk
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageTk
from PIL import ImageOps
from tkinter import filedialog
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pithermalcam as ptc

import queue
import sounddevice as sd 
import random
import sys
import subprocess
import numpy as np
import random
import cv2
import csv

audio_queue = queue.Queue()
y_data = np.zeros(100)

#Dynamically get file paths
current_file = Path(__file__) # Path to this file
project_root = current_file.parent.parent # Path to Automated-Survival-Detection-Vehicle
sys.path.insert(0, str(project_root))

#update clock info
def updateclock():
    eastern = ZoneInfo('America/New_York')
    currentTime = datetime.now(eastern)
    timeString = currentTime.strftime('%H:%M:%S.%f')[:-3]
    clockLabel.config(text=timeString)
    root.after(1000, updateclock)

#agv map simulation
def trackingMap():
    mapCanvas.delete("all")
    
    #for grid lines
    for i in range(0, 500, 50):
        mapCanvas.create_line(i, 0, i, 500, fill="gray")
        mapCanvas.create_line(0, i, 500, i, fill="gray")
    
    #simulate the agv current pos
    mapCanvas.create_oval(240, 240, 260, 260, fill="white", outline="blue", width=2, tags="AGV")
    mapCanvas.create_text(250, 270, text="AGV", fill="white", font=("Helvetica", 10, "bold"))

    #simulate surivior locations
    survivors = [(100, 100), (400, 150), (350, 400)]
    for x, y in survivors:
        mapCanvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="red", outline="white", width=2)

    root.after(1000, trackingMap)

#add notification to notification list
def addNotification(notification):
    notificationList.insert(END, notification)

#view notification in as new window
def viewNotification(event):
    index = notificationList.curselection()
    if index:
        selectedNotification = notificationList.get(index)
        
        #window for detailed notification
        top = Toplevel()
        top.title("Full Notification")
        top.geometry("400x200")

        #notficiation window
        notificationWindow = ttk.Label(top, text=selectedNotification, font=("Helvetica", 12))
        notificationWindow.pack(padx=20, pady=20)

#simulate battery level changing
def updateBatteryLevel():
    batteryValue = random.randint(0,100)
    batteryProgressBar['value'] = batteryValue
    batteryLabel.config(text=f'Battery: {batteryValue}%')

    root.after(5000, updateBatteryLevel)

#simulate heartbeat data update
def updateHeartbeatData():
    heartbeatValue = random.randint(60, 100)
    heartbeatDataEntry.delete(0, END)
    heartbeatDataEntry.insert(0, str(heartbeatValue))

    root.after(1000, updateHeartbeatData)

#simulate vocal data
def updateVocalData():
    vocalValue = random.choice(['Hello', 'Yes', 'No'])
    vocalDataEntry.delete(0, END)
    vocalDataEntry.insert(0, vocalValue)

    root.after(3000, updateVocalData)

# Function to handle vocal button press
def playVocalSound():
    try:
        subprocess.run(['python', project_root/"Sound/soundDriver.py"], check=True)
        addNotification("Sound played successfully")
    except Exception as e:
        error_message = f"Error playing sound: {str(e)}"
        addNotification(error_message)

#simulate body temp data
def updateBodyTempData():
    bodytempValue = round(random.uniform(36.0, 37.5), 1)
    bodytempDataEntry.delete(0,END)
    bodytempDataEntry.insert(0, str(bodytempValue))

    root.after(5000, updateBodyTempData)

#agv movement algorithms
def forward():
    print('AGV forward movement')
def backward():
    print('AGV backward movement')
def left():
    print('AGV left movement')
def right():
    print('AGV right movement')

def cameraFeed():
    global imgTk
    ret, frame = camera.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgTk = ImageTk.PhotoImage(image=img)
        cameraLabel.imgTk = imgTk
        cameraLabel.config(image=imgTk)
    cameraLabel.after(10, cameraFeed)

def readThermalCamera():
    thermal_data = ptc.display_camera_live()
    return thermal_data

def thermalCameraFeed():
    global thermalImgTk
    thermal_data = readThermalCamera()

    # 8-bit image
    thermal_img = Image.fromarray(thermal_data.astype('uint8'))
    thermal_img = ImageOps.fit(thermal_img, (425, 250)) 
    
    thermalImgTk = ImageTk.PhotoImage(image=thermal_img)
    thermalCameraLabel.imgTk = thermalImgTk
    thermalCameraLabel.config(image=thermalImgTk)
    
    thermalCameraLabel.after(1000, thermalCameraFeed)

#logging data from sensors
notificationDetails = {}
def logSensorData():
    try:
        heartbeat = heartbeatDataEntry.get()
        vocal = vocalDataEntry.get()
        bodyTemp = bodytempDataEntry.get()

        if not heartbeat or not vocal or not bodyTemp:
            raise ValueError('Error check..')

        eastern = ZoneInfo('America/New_York')
        currentTime = datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S')
        location = 'Random Location'

        dataTable.insert('', 'end', values=(location, currentTime, heartbeat, vocal, bodyTemp))

        shortMessage = "Data logged successfully"        
        fullMessage = f"Data logged successfully at {currentTime} - {heartbeat} bpm, {vocal}, {bodyTemp} °C"

        notificationDetails[shortMessage] = fullMessage
        addNotification(shortMessage)
        
    except Exception as e:
        errorMessage='Error in logging data'
        addNotification(errorMessage)
        addNotification(f'Error: {str(e)}')

        notificationDetails[shortMessage] = fullMessage
        addNotification(shortMessage)

def exportData():
    filePath = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])


    if filePath:
        with open(filePath, mode='w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(['Location', 'Time','Heartbeat', 'Vocal','Body Temp °C'])

            for row in dataTable.get_children():
                rowData = dataTable.item(row)['values']
                writer.writerow(rowData)

        addNotification('Data Exported successfully')
    
#main window
root = Tk()
root.title('AGV-HSD')
root.geometry('1000x600')
root.minsize(1050, 800)
root.maxsize(1050, 800)
root.config(bg='black')

#tabs frame
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Create tabs
updatesTab = ttk.Frame(notebook)
trackingTab = ttk.Frame(notebook)
survivorTab = ttk.Frame(notebook)

#add tabs to notebook
notebook.add(updatesTab, text='AGV Status Updates')
notebook.add(trackingTab, text='Real-Time AGV Tracking')
notebook.add(survivorTab, text='Real-Time Survivor Detection Status')

#clock label
clockLabel = ttk.Label(root, text='', font=('Helvetica', 18))
clockLabel.place(x=1050, y=0)
updateclock()

#AGV Status Updates tab
#left frame

#notification bar with scroll bar in left panel
leftFrame = ttk.Frame(updatesTab)
leftFrame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

notificationsLabel = ttk.Label(leftFrame, text='Notifications', font=('Helvetica', 14, 'bold'))
notificationsLabel.pack(pady=(0, 5), anchor='w')

scrollbar = ttk.Scrollbar(leftFrame, orient=VERTICAL)
scrollbar.pack(side=RIGHT, fill=Y)

#list of notifications in leftFrame
notificationList = Listbox(leftFrame, yscrollcommand=scrollbar.set, width=25, height=15)
notificationList.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar.config(command=notificationList.yview)

#right frame
#data section
rightFrame = ttk.Frame(updatesTab)
rightFrame.grid(row=0, column=1, sticky='nsew', padx=10, pady=0)

heartbeatFrame = ttk.Frame(rightFrame)
heartbeatFrame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

heartbeatLabel = ttk.Label(heartbeatFrame, text='Heartbeat Data')
heartbeatLabel.grid(row=1, column=0, padx=5, pady=(10,0), sticky='s')

heartbeatDataEntry = ttk.Entry(heartbeatFrame, width=10)
heartbeatDataEntry.grid(row=2, column=0, padx=10, pady=(0,5), sticky='n')

updateHeartbeatData()

#vocal data
vocalFrame = ttk.Frame(rightFrame)
vocalFrame.grid(row=3, column=0, padx=10, pady=(0,10), sticky='ew')

vocalLabel = ttk.Label(vocalFrame, text='Vocal Response')
vocalLabel.grid(row=1, column=0, padx=5, pady=(10,0), sticky='s')

vocalDataEntry = ttk.Entry(vocalFrame, width=10)
vocalDataEntry.grid(row=2, column=0, padx=10, pady=(0,5), sticky='n')

updateVocalData()

#send vocal response
vocalButtonFrame = ttk.Frame(rightFrame)
vocalButtonFrame.grid(row=3, column=0, padx=(100,10), pady=(60,10), sticky='ns')

sendVocalsButton = ttk.Button(vocalButtonFrame, text="Send Vocal Data", command=playVocalSound)
sendVocalsButton.grid(row=0, column=0, padx=(25,5), pady=(0,10), sticky='n')

#waveform
waveformFrame = ttk.Frame(rightFrame)
waveformFrame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='w')

waveFormLabel = ttk.Label(waveformFrame, text='Vocal Waves')
waveFormLabel.grid(row=0, column=0, padx=5, pady=5, sticky='w')

fig = Figure(figsize=(3.5, 0.75), dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim(-1, 1)
ax.set_xlim(0, 100)
ax.set_xticks([])
ax.set_yticks([])
line, = ax.plot(np.arange(100), y_data, lw=1, color='black')

canvas = FigureCanvasTkAgg(fig, master=waveformFrame)
canvas.get_tk_widget().grid(row=1, column=0, padx=5, pady=5, sticky='ew')

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
        addNotification(status)
    
    global audio_queue
    audio_queue.put(np.squeeze(indata))
    # print(f"Audio Data Shape: {indata.shape}")

def updateWaveform():
    global y_data
    if not audio_queue.empty():
        audio_data = audio_queue.get()
        
        # Clip or pad data to exactly 100 samples
        y_data = np.pad(audio_data, (0, max(0, 100 - len(audio_data))), mode='constant')[:100]
    else:
        y_data = np.zeros(100)
    
    line.set_ydata(y_data)
    canvas.draw()
    
    root.after(50, updateWaveform)

line, = ax.plot(np.arange(100), y_data, lw=1, color='black')
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=44100, blocksize=100)

try:
    stream.start()
except Exception as e:
    print(f"Failed to stream audio: {e}")


updateWaveform()

#body temp data
bodytempFrame = ttk.Frame(rightFrame)
bodytempFrame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

bodytempLabel = ttk.Label(bodytempFrame, text='Body Temp °C  ')
bodytempLabel.grid(row=1, column=0, padx=5, pady=(10,0), sticky='s')

bodytempDataEntry = ttk.Entry(bodytempFrame, width=10)
bodytempDataEntry.grid(row=2, column=0, padx=10, pady=(0,5), sticky='n')

updateBodyTempData()

#agv location data
locationFrame = ttk.Frame(rightFrame)
locationFrame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

locationLabel = ttk.Label(locationFrame, text='AGV Location')
locationLabel.grid(row=1, column=0, padx=5, pady=(10,0), sticky='s')

locationDataEntry = ttk.Entry(locationFrame, width=10)
locationDataEntry.grid(row=2, column=0, padx=10, pady=(0,5), sticky='n')

updateBodyTempData()

#agv manual movement arrows
movementFrame = ttk.Frame(rightFrame)
movementFrame.grid(row=2, column=1, rowspan=2, padx=10, pady=10, sticky='nsew')

movementLabel = ttk.Label(movementFrame, text='Manual AGV Control')
movementLabel.grid(row=0, column=1, columnspan=3, padx=0, pady=(10, 0), sticky='w')

arrowFrame = ttk.Frame(movementFrame)
arrowFrame.grid(row=1, column=0, columnspan=3, padx=(35,0), pady=5, sticky='w')

forwardButton = Button(arrowFrame, text='Forward', width=3, height=2, command=forward)
forwardButton.grid(row=2, column=1, padx=5, pady=(0,5))

backwardButton = Button(arrowFrame, text='Backward', width=3, height=2, command=backward)
backwardButton.grid(row=4, column=1, padx=5, pady=5)

leftButton = Button(arrowFrame, text='Left', width=3, height=2, command=left)
leftButton.grid(row=3, column=0, padx=5, pady=5)

rightButton = Button(arrowFrame, text='Right', width=3, height=2, command=right)
rightButton.grid(row=3, column=2, padx=5, pady=5)

#mechanical arm
armFrame = ttk.Frame(rightFrame)
armFrame.grid(row=0, column=1, padx=85, pady=10, sticky='nsew')

armLabel = ttk.Label(armFrame, text='Mechanical Arm Control')
armLabel.grid(row=0, column=0, padx=10, pady=(10,0), sticky='w')

#bottom frame
#battery progress bar
bottomFrame = ttk.Label(updatesTab)
bottomFrame.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)

batteryLabel = ttk.Label(bottomFrame, text='Battery: 0%')
batteryLabel.grid(row=0, column=0, padx=(0, 10), sticky='w')

batteryProgressBar = ttk.Progressbar(bottomFrame, orient=HORIZONTAL, length=200, mode='determinate')
batteryProgressBar.grid(row=0, column=1, padx=(0,10), sticky='w')

updateBatteryLevel()

#data log button
collectDataButton = tk.Button(bottomFrame, text="Log Data", command=logSensorData)
collectDataButton.grid(row=0, column=2, padx=(10, 0), sticky='e')
collectDataButton.config(font=('Arial', 14))
collectDataButton.grid_configure(ipadx=5, ipady=10)

#agv tracking tab
trackingLeftFrame = Frame(trackingTab)
trackingLeftFrame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

cameraLabel = Label(trackingLeftFrame, text='Label', fg='white', bg='black', width=350, height=20)
cameraLabel.pack(fill='both', expand=True)

thermalCameraLabel = Label(trackingLeftFrame, text='Thermal Camera Feed', fg='white', bg='black', width=350, height=50, pady=0)
thermalCameraLabel.pack(fill='both', expand=True)

thermalCameraFeed()

mapFrame = Frame(trackingTab)
mapFrame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

mapCanvas = Canvas(mapFrame, width=300, height=500, bg='black')
mapCanvas.pack(fill='both', expand=True)

camera = cv2.VideoCapture(0)
cameraFeed()
trackingMap()

#survivor detection tab
tableFrame = ttk.Frame(survivorTab)
tableFrame.pack(fill='both', expand=True, padx=10, pady=10)

dataTable = ttk.Treeview(tableFrame, columns=('Location', 'Time', 'Heartbeat', 'Vocal', 'Body Temp °C'), show='headings')
dataTable.pack(fill='both', expand=True)

dataTable.heading('Location', text='Location')
dataTable.heading('Time', text='Time')
dataTable.heading('Heartbeat', text='Heartbeat')
dataTable.heading('Vocal', text='Vocal')
dataTable.heading('Body Temp °C', text='Body Temp')

dataTable.column('Location', width=200, anchor='center')
dataTable.column('Time', width=150, anchor='center')
dataTable.column('Heartbeat', width=100, anchor='center')
dataTable.column('Vocal', width=100, anchor='center')
dataTable.column('Body Temp °C', width=100, anchor='center')

exportButton = ttk.Button(survivorTab, text='Export Data', command = exportData)
exportButton.pack(pady=10)

def viewNotification(event):
    index = notificationList.curselection()
    if index:
        shortMessage = notificationList.get(index)
        fullMessage = notificationDetails.get(shortMessage, 'No detailed message available.')
        
        # Window for detailed notification
        top = Toplevel()
        top.title("Full Notification")
        top.geometry("400x200")

        # Notification window displaying full message
        notificationWindow = ttk.Label(top, text=fullMessage, font=("Helvetica", 12))
        notificationWindow.pack(padx=20, pady=20)

# Bind double-click event to open detailed notification
notificationList.bind("<Double-1>", viewNotification)

#for window scaling
updatesTab.columnconfigure(1, weight=1)
updatesTab.rowconfigure(0, weight=1)


rightFrame.rowconfigure((0,1,2,3, 4), weight=1, uniform='column')
rightFrame.columnconfigure((0,1), weight=1)
arrowFrame.columnconfigure((0,1,2), weight=1)

trackingTab.columnconfigure(0, weight=1)
trackingTab.columnconfigure(1, weight=2)
trackingTab.rowconfigure(0,weight=1)

bottomFrame.columnconfigure(0, weight=0)
bottomFrame.columnconfigure(1, weight=1)
bottomFrame.columnconfigure(2, weight=0)

def main():
    root.mainloop()

if __name__ == "__main__":
    main()

