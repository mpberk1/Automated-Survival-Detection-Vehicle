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
#import pithermalcam as ptc

import speech_recognition as sr
import queue
import sounddevice as sd 
import importlib.util

module_path = "/home/agv/Desktop/Automated-Survival-Detection-Vehicle/PiThermalCam/piThermCam.py"
spec = importlib.util.spec_from_file_location("piThermCam", module_path)
piThermCam = importlib.util.module_from_spec(spec)
spec.loader.exec_module(piThermCam)

thermal_camera = piThermCam.pithermalcam()
import random
import sys
import subprocess
import numpy as np
import random
import cv2
import csv
import threading

#global variables
audio_queue = queue.Queue()
y_data = np.zeros(100)
stream = None

#Dynamically get file paths
current_file = Path(__file__) # Path to this file
project_root = current_file.parent.parent # Path to Automated-Survival-Detection-Vehicle
sys.path.insert(0, str(project_root))

# deviceDriver_dir = project_root / "DeviceDrivers"
# sys.path.append(str(deviceDriver_dir))
# import MotorControl

gpsDir =project_root / "GPS"
sys.path.append(str(gpsDir))

#update clock info
def updateclock():
    eastern = ZoneInfo('America/New_York')
    currentTime = datetime.now(eastern)
    timeString = currentTime.strftime('%H:%M:%S.%f')[:-3]
    clockLabel.config(text=timeString)
    root.after(1000, updateclock)

def trackingMap():
    mapCanvas.delete("all")

    # Get dynamic canvas size
    canvas_width = mapCanvas.winfo_width()  
    canvas_height = mapCanvas.winfo_height()  

    # Ensure valid dimensions
    if canvas_width == 1 or canvas_height == 1:  # Prevents issues when canvas hasn't been drawn yet
        root.after(100, trackingMap)
        return  

    # Draw grid lines dynamically
    grid_size = 50  
    for i in range(0, canvas_width, grid_size):  
        mapCanvas.create_line(i, 0, i, canvas_height, fill="gray")  # Vertical lines
    for i in range(0, canvas_height, grid_size):  
        mapCanvas.create_line(0, i, canvas_width, i, fill="gray")  # Horizontal lines

    # Default AGV coordinates if not available
    if lat is None or long is None:
        agv_lat, agv_long = 0, 0  # Center at (0,0) if no GPS yet
    else:
        agv_lat, agv_long = lat, long

    # Center of the canvas for AGV
    agv_x = canvas_width // 2
    agv_y = canvas_height // 2

    # Draw AGV position in center
    mapCanvas.create_oval(agv_x - 10, agv_y - 10, agv_x + 10, agv_y + 10, 
                          fill="white", outline="blue", width=3, tags="AGV")

    # Display AGV coordinates
    mapCanvas.create_text(agv_x, agv_y - 15, text=f"({agv_lat:.4f}, {agv_long:.4f})", 
                          fill="white", font=("Helvetica", 14, "bold"))

    # Label AGV
    mapCanvas.create_text(agv_x, agv_y + 15, text="AGV", fill="white", font=("Helvetica", 14, "bold"))

    # Simulated survivor locations (relative positions)
    # Example survivors around AGV
    survivors = [(-0.001, -0.001), (0.002, -0.0015), (0.0015, 0.002)]  # Offset in degrees (lat/long difference)

    # Scaling factor to adjust how far survivors are from AGV on screen
    scale_factor = 100000  # Adjust for your map scale (higher = closer)

    for s_lat_offset, s_long_offset in survivors:
        # Compute survivor relative position in pixels
        offset_x = s_long_offset * scale_factor
        offset_y = -s_lat_offset * scale_factor  # Negative to invert Y-axis for canvas

        survivor_x = agv_x + offset_x
        survivor_y = agv_y + offset_y

        mapCanvas.create_oval(survivor_x - 10, survivor_y - 10, survivor_x + 10, survivor_y + 10, 
                              fill="red", outline="white", width=2)

    root.after(1000, trackingMap)

#add notification to notification list
def addNotification(short_message, full_message=None):
    if full_message is None:
        notificationList.insert(END, short_message)
    else:
        notificationList.insert(END, short_message)
        notificationDetails[short_message] = full_message

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

lat, long = None, None
def updateAGVLocation():
    global lat, long
    import GPS
    agvLocation = GPS.gps_locator()
    if agvLocation and isinstance(agvLocation, tuple):
        city, state, lat, long = agvLocation
        locationDataEntry.delete(0, END)
        locationDataEntry.insert(0, f"{city}, {state}: {lat}, {long}")
        pointAEntry.delete(0, END)
        pointAEntry.insert(0, f"{lat}, {long}")
        
    root.after(1000, updateAGVLocation)

#simulate heartbeat data update
def updateHeartbeatData():
    heartbeatValue = random.randint(60, 100)
    heartbeatDataEntry.delete(0, END)
    heartbeatDataEntry.insert(0, str(heartbeatValue))

    root.after(1000, updateHeartbeatData)

#update vocal data
def updateVocalData():

    def recognize_speech():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            print("Listening.")
            try:
                audio = recognizer.listen(source)
                vocalValue = recognizer.recognize_google(audio)
                addNotification("Voice detected")
            except sr.UnknownValueError:
                vocalValue = ""
            except sr.RequestError:
                vocalValue = "API error"

        root.after(0, lambda: vocalDataEntry.delete(0, END))
        root.after(0, lambda: vocalDataEntry.insert(0, vocalValue))
    threading.Thread(target=recognize_speech, daemon=True).start()
    root.after(3000, updateVocalData)

# Function to handle vocal button press
def playVocalSound():
    try:
        subprocess.run(['python', project_root/"Sound/soundDriver.py"], check=True)
        addNotification("Sound played successfully","Sound played successfully")
    except Exception as e:
        error_message = f"Error playing sound: {str(e)}"
        addNotification(error_message,error_message)

#simulate body temp data
def updateBodyTempData():
    bodytempValue = round(random.uniform(36.0, 37.5), 1)
    bodytempDataEntry.delete(0,END)
    bodytempDataEntry.insert(0, str(bodytempValue))

    root.after(5000, updateBodyTempData)

#agv movement algorithms
button_pressed = False
def forward():
    if button_pressed:
        # MotorControl.move_forward(duration=2)
        addNotification("AGV Forward Movement")
        root.after(100,forward)
def backward():
    if button_pressed:
        # MotorControl.move_reverse(duration=2)
        addNotification("AGV Backward Movement")
        root.after(100,backward)
def left():
    if button_pressed:
        # MotorControl.turn_left(duration=2)
        addNotification("AGV Left Movement")
        root.after(100,left)
def right():
    if button_pressed:
        # MotorControlß.turn_right(duration=2)
        addNotification("AGV Right Movement")
        root.after(100,right)
def stop():
    if button_pressed:
        #MotorControl.stop()
        addNotification("AGV Stop")

def on_press(direction):
    global button_pressed
    button_pressed = True
    direction()

def on_release():
    global button_pressed
    button_pressed = False
    stop()


def cameraFeed():
    global imgTk
    ret, frame = camera.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (CAMERA_WIDTH, CAMERA_HEIGHT))
        img = Image.fromarray(frame)
        imgTk = ImageTk.PhotoImage(image=img)
        cameraLabel.imgTk = imgTk
        cameraLabel.config(image=imgTk)
    cameraLabel.after(10, cameraFeed)


#logging data from sensors
#validate input
def validate_input(value, expected_type):
    try:
        if expected_type=="int":
            return int(value)
        elif expected_type=="float":
            return float(value)
    except ValueError:
        return None

#log data
notificationDetails = {}
def logSensorData():
    global lat, long
    try:
        heartbeat = validate_input(heartbeatDataEntry.get(), "int")
        vocal = vocalDataEntry.get()
        bodyTemp = validate_input(bodytempDataEntry.get(), "float")

        if bodyTemp is None:
            raise ValueError('Invalid Input')
        if heartbeat=="":
            heartbeat="none"
        if vocal =="":
            vocal="none"

        eastern = ZoneInfo('America/New_York')
        currentTime = datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S')
        location = f"{lat}, {long}"

        try:
            dataTable.insert('', 'end', values=(location, currentTime, heartbeat, vocal, bodyTemp))
        except Exception as e:
            print(f"Error: {e}")
            addNotification(f"Error: {e}",f"Error: {e}")

        shortMessage = "Data logged successfully"        
        fullMessage = f"Data logged successfully at {currentTime} - {heartbeat} bpm, {vocal}, {bodyTemp} °C"
        addNotification(shortMessage,fullMessage)
        
    except Exception as e:
        addNotification('Error in logging data', f"Error: {str(e)}")

def exportData():
    filePath = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])

    if filePath:
        with open(filePath, mode='w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(['Location', 'Time','Heartbeat', 'Vocal','Body Temp °C'])

            for row in dataTable.get_children():
                rowData = dataTable.item(row)['values']
                writer.writerow(rowData)

        addNotification('Data Exported successfully','Data Exported successfully')
    
#main window
root = Tk()
root.title('AGV-HSD')
root.geometry('1000x600')
root.minsize(1050, 700)
# root.maxsize(1050, 800)
root.resizable(True, True)
root.config(bg='black')

#tabs frame
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# CREATE TABS
updatesTab = ttk.Frame(notebook)
trackingTab = ttk.Frame(notebook)
survivorTab = ttk.Frame(notebook)
pathTab = ttk.Frame(notebook)

#add tabs to notebook
notebook.add(updatesTab, text='AGV Status Updates')
notebook.add(trackingTab, text='Real-Time AGV Tracking')
notebook.add(survivorTab, text='Real-Time Survivor Detection Status')
notebook.add(pathTab, text='AGV Path')

#clock label
clockLabel = ttk.Label(root, text='', font=('Helvetica', 18))
clockLabel.place(x=850, y=0)
updateclock()

#AGV STATUS UPDATES TAB
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

#microphone buttons

play_icon = tk.PhotoImage(file=project_root/"GUI/play_icon.png")
play_button = tk.Button(vocalFrame, image=play_icon, command=lambda: print("Button"),  borderwidth=0)
play_button.grid(row=3, column=0, padx=(15,0), pady=0, sticky='nw')

pause_icon = tk.PhotoImage(file=project_root/"GUI/pause_icon.png")
pause_button = tk.Button(vocalFrame, image=pause_icon, command=lambda: print("Button"),  borderwidth=0)
pause_button.grid(row=3, column=0, padx=(60,0), pady=0, sticky='nw')

updateVocalData()

#send vocal response
vocalButtonFrame = ttk.Frame(rightFrame)
vocalButtonFrame.grid(row=3, column=0, padx=(100,10), pady=(40,10), sticky='ns')

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
        print(f"Audio Status: {status}")
        addNotification(f"Audio Status: {status}",f"Audio Status: {status}")
    
    audio_data = indata[:,0]
    # global audio_queue
    audio_queue.put(audio_data)
    # print(f"Audio Data Shape: {indata.shape}")

def updateWaveform():
    global y_data
    if not audio_queue.empty():
        audio_data = audio_queue.get()

        audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data

        # Clip or pad data to exactly 100 samples
        y_data = np.pad(audio_data, (0, max(0, 100 - len(audio_data))), mode='constant')[:100]
    else:
        y_data = np.zeros(100)
    
    line.set_ydata(y_data)
    canvas.draw()
    
    root.after(50, updateWaveform)

def start_audio_stream():
    global stream
    try:
        stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=44100, blocksize=100)
        stream.start()
        print("Audio stream started")
        addNotification("Audio stream started","Audio stream started")
    except Exception as e:
        print(f"Failed to stream audio: {e}")
        addNotification(f"Audio Stream Error: {e}",f"Audio Stream Error: {e}")

# line, = ax.plot(np.arange(100), y_data, lw=1, color='black')
# stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=44100, blocksize=100)

# try:
#     stream.start()
# except Exception as e:
#     print(f"Failed to stream audio: {e}")

start_audio_stream()
updateWaveform()

# Update the thermal camera feed function
def update_thermal_camera():
    global thermalImgTk

    # Get the thermal frame from the camera
    thermal_frame = thermal_camera.get_image_frame_for_gui()
    
    # Convert the frame to a Tkinter-compatible format
    thermal_img = Image.fromarray(cv2.cvtColor(thermal_frame, cv2.COLOR_BGR2RGB))
    thermal_img = thermal_img.resize((425, 250))  # Resize to match the label size
    thermalImgTk = ImageTk.PhotoImage(image=thermal_img)

    # Update the label with the new image
    ThermalCameraLabel.imgTk = thermalImgTk
    ThermalCameraLabel.config(image=thermalImgTk)

    # Schedule the next update (100ms delay)
    ThermalCameraLabel.after(100, update_thermal_camera)

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
locationLabel.grid(row=1, column=0, padx=10, pady=(10,0), sticky='w')

locationDataEntry = ttk.Entry(locationFrame, width=50)
locationDataEntry.grid(row=2, column=0, padx=10, pady=(0,5), sticky='n')


#agv manual movement arrows
movementFrame = ttk.Frame(rightFrame)
movementFrame.grid(row=2, column=1, rowspan=2, padx=10, pady=10, sticky='nsew')

movementLabel = ttk.Label(movementFrame, text='Manual AGV Control')
movementLabel.grid(row=0, column=1, columnspan=3, padx=0, pady=(10, 0), sticky='w')

arrowFrame = ttk.Frame(movementFrame)
arrowFrame.grid(row=1, column=0, columnspan=3, padx=(35,0), pady=5, sticky='w')

forwardButton = Button(arrowFrame, text='Forward', width=3, height=2)
forwardButton.grid(row=2, column=1, padx=5, pady=(0,5))
forwardButton.bind("<ButtonPress>", lambda event: on_press(forward))
forwardButton.bind("<ButtonRelease>", lambda event: on_release())

backwardButton = Button(arrowFrame, text='Backward', width=3, height=2)
backwardButton.grid(row=4, column=1, padx=5, pady=5)
backwardButton.bind("<ButtonPress>", lambda event: on_press(backward))
backwardButton.bind("<ButtonRelease>", lambda event: on_release())

leftButton = Button(arrowFrame, text='Left', width=3, height=2)
leftButton.grid(row=3, column=0, padx=5, pady=5)
leftButton.bind("<ButtonPress>", lambda event: on_press(left))
leftButton.bind("<ButtonRelease>", lambda event: on_release())

rightButton = Button(arrowFrame, text='Right', width=3, height=2)
rightButton.grid(row=3, column=2, padx=5, pady=5)
rightButton.bind("<ButtonPress>", lambda event: on_press(right))
rightButton.bind("<ButtonRelease>", lambda event: on_release())

stopButton = Button(arrowFrame, text='stop', width=3, height=2)
stopButton.grid(row=3, column=1, padx=5, pady=5)

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

#AGV REAL-TIME UPDATES TAB
#camera frame
CAMERA_WIDTH=450
CAMERA_HEIGHT=300

cameraFrame = ttk.Frame(trackingTab, width=10, height=10)
cameraFrame.grid(row=0, column=0, padx=0, pady=(10, 0), sticky='news')

cameraTextLabel = ttk.Label(cameraFrame, text='AGV Camera', padding=(10, 5), font=("Arial", 16, "bold"))
cameraTextLabel.grid(row=0, column=0, sticky='nsew')

cameraLabel = Label(cameraFrame, text='Camera', fg='white', bg='black', width=CAMERA_WIDTH, height=CAMERA_HEIGHT)
cameraLabel.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0,10))

camera = cv2.VideoCapture(0)
cameraFeed()

#thermal camera frame
ThermalCameraFrame = ttk.Frame(trackingTab, width=10, height=10)
ThermalCameraFrame.grid(row=1, column=0, padx=0, pady=10, sticky='news')

ThermalCameraTextLabel = ttk.Label(ThermalCameraFrame, text='AGV Thermal Camera', padding=(10, 5), font=("Arial", 16, "bold"))
ThermalCameraTextLabel.grid(row=0, column=0, sticky='nsew')

ThermalCameraLabel = Label(ThermalCameraFrame, text='OFFLINE', fg='red', bg='black', width=50, height=18)
ThermalCameraLabel.grid(row=1, column=0, sticky='news', padx=10, pady=(0,10))

ThermalCameraLabel = ttk.Label(trackingTab)
ThermalCameraLabel.grid(row=0, column=0, padx=10, pady=10)

# Start the thermal camera feed when the application runs
update_thermal_camera()

#thermalCameraFeed()

#map frame
mapFrame = ttk.Frame(trackingTab)
mapFrame.grid(row=0, column=1, rowspan=2, padx=0, pady=10, sticky='news')

AGVTextLabel = ttk.Label(mapFrame, text='AGV Environment Map', padding=(10, 5), font=("Arial", 16, "bold"))
AGVTextLabel.grid(row=0, column=0, sticky='nsew')

mapCanvas = Canvas(mapFrame, bg='black', width=500, height=10)
mapCanvas.grid(row=1, column=0, rowspan=2, sticky='news', padx=10, pady=(0,10))

trackingMap()

#SURVIVOR DETECTION TAB
#table
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

#AGV PATH TAB
#path frame
#pathFrame = ttk.Frame(pathTab)
#pathFrame.pack(fill='both', expand=True, padx=10, pady=10)

pathLabel = ttk.Label(pathTab, text='AGV Point A to Point B', padding=(10, 5), font=("Arial", 16, "bold"))
pathLabel.grid(row=0, column=0, padx=5, pady=(0, 10), sticky='s')

# Point A is AGV location while Point B is destination
pointALabel = ttk.Label(pathTab, text='Current Location (latitude, longitude)', padding=(10, 5), font=("Arial", 16, "bold"))
pointALabel.grid(row=2, column=0, padx=5, pady=(10,0), sticky='s')
pointAEntry = ttk.Entry(pathTab, width=50)
pointAEntry.grid(row=3, column=0, padx=5, pady=(0,5), sticky='n')

pointBLabel = ttk.Label(pathTab, text='Enter Destination (latitude, longitude)', padding=(10, 5), font=("Arial", 16, "bold"))
pointBLabel.grid(row=5, column=0, padx=5, pady=(10,0), sticky='s')
#pathLabel.grid(row=1, column=0, padx=5, pady=(10,0), sticky='s')
pointBEntry = ttk.Entry(pathTab, width=50)
pointBEntry.grid(row=6, column=0, padx=5, pady=(0,5), sticky='n')

distanceLabel = ttk.Label(pathTab, text='Resulting Distance in kilometers', padding=(10, 5), font=("Arial", 16, "bold"))
distanceLabel.grid(row=7, column=0, padx=5, pady=(10,0), sticky='s')
distanceDisplay = ttk.Entry(pathTab, width=50)
distanceDisplay.grid(row=8, column=0, padx=5, pady=(0,5), sticky='n')

directionLabel = ttk.Label(pathTab, text='Resulting Direction Clockwise From North (degrees)', padding=(10, 5), font=("Arial", 16, "bold"))
directionLabel.grid(row=9, column=0, padx=5, pady=(10,0), sticky='s')
directionDisplay = ttk.Entry(pathTab, width=50)
directionDisplay.grid(row=10, column=0, padx=5, pady=(0,5), sticky='n')

#Calculate Direction And Distance
def calculateVector():
    try:
        pointA = pointAEntry.get().split(',')
        pointB = pointBEntry.get().split(',')

        if len(pointA) != 2 or len(pointB) != 2:
            raise ValueError("Invalid input format. Use (latitude, longitude)")

        latA, longA = map(float, pointA)
        latB, longB = map(float, pointB)

        # Calculate distance using Haversine formula
        R = 6371  # Radius of the Earth in kilometers
        dlat = np.radians(latB - latA)
        dlong = np.radians(longB - longA)
        a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(latA)) * np.cos(np.radians(latB)) * np.sin(dlong / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = R * c  # Distance in kilometers
        
        # Calculate direction in degrees clockwise from North
        y = np.sin(dlong) * np.cos(np.radians(latB))
        x = np.cos(np.radians(latA)) * np.sin(np.radians(latB)) - np.sin(np.radians(latA)) * np.cos(np.radians(latB)) * np.cos(dlong)
        direction = (np.degrees(np.arctan2(y, x)) + 360) % 360  

        # Display results
        distanceDisplay.delete(0, END)
        distanceDisplay.insert(0, f"{distance:.4f}")
        directionDisplay.delete(0, END)
        directionDisplay.insert(0, f"{direction:.2f}")
        #distanceDisplay.config(text=f"Distance: {distance:.4f} earth degrees")
        #directionDisplay.config(text=f"Direction: {direction:.2f} degrees clockwise from North")
        return distance, direction
    except Exception as e:
        distanceDisplay.delete(0, END)
        distanceDisplay.insert(0, f"Error: {str(e)}")
        directionDisplay.delete(0, END)
        directionDisplay.insert(0, pointA)
        #distanceDisplay.config(text=f"Error: {str(e)}")
        #directionDisplay.config(text=f"Error: {str(e)}")

calculateDistanceDirection = tk.Button(pathTab, text="Get Distance & Direction", command=calculateVector)
calculateDistanceDirection.grid(row=11, column=0, padx=(10, 0), pady=(10, 0), sticky='n')
calculateDistanceDirection.config(font=('Arial', 14))
calculateDistanceDirection.grid_configure(ipadx=5, ipady=10)

updateAGVLocation()

# view notification
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

mapFrame.grid_rowconfigure(0, weight=0)
mapFrame.grid_rowconfigure(1, weight=1)
mapFrame.grid_columnconfigure(0, weight=1)

trackingTab.grid_rowconfigure(0, weight=1)
trackingTab.grid_rowconfigure(1, weight=1)
trackingTab.grid_columnconfigure(0, weight=1)
trackingTab.grid_columnconfigure(1, weight=1)

def main():
    root.mainloop()

if __name__ == "__main__":
    main()

