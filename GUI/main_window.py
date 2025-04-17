import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import Canvas
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Notebook, Entry, Label, Button, Frame, Scrollbar, Treeview
from ttkbootstrap import Style
from ttkbootstrap.scrolled import ScrolledText
from tkinter import Listbox, RIGHT, LEFT, Y, BOTH, VERTICAL, FLAT 
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageTk
from PIL import ImageOps
import pickle
from tkinter import filedialog
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import socket

import speech_recognition as sr
import queue
import sounddevice as sd 
import importlib.util
import random
import sys
import subprocess
import numpy as np
import random
import cv2
import csv
import threading

#Dynamically get file paths
current_file = Path(__file__) # Path to this file
project_root = current_file.parent.parent # Path to Automated-Survival-Detection-Vehicle
sys.path.insert(0, str(project_root))

# module_path = project_root/"PiThermalCam/piThermCam.py"
# spec = importlib.util.spec_from_file_location("piThermCam", module_path)
# piThermCam = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(piThermCam)

# thermal_camera = piThermCam.pithermalcam()

#global variables
audio_queue = queue.Queue()
y_data = np.zeros(100)
stream = None

# deviceDriver_dir = project_root / "DeviceDrivers"
# sys.path.append(str(deviceDriver_dir))
# import MotorControl

gpsDir =project_root / "GPS"
sys.path.append(str(gpsDir))

def init_socket_connection():
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("10.33.228.31", 5000))
        print("Connected to server.")
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        client_socket = None

#function to send commmands to the server:
def send_command_to_server(command):
    global client_socket
    try:
        if client_socket:
            client_socket.sendall(command.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print("Server response:", response)
        else:
            print("Socket not connected.")
    except Exception as e:
        print(f"Failed to send command: {e}")
init_socket_connection()
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
    mapCanvas.create_oval(agv_x - 10, agv_y - 10, agv_x + 10, agv_y + 10, fill="white", outline="blue", width=3, tags="AGV")

    # Display AGV coordinates
    mapCanvas.create_text(agv_x, agv_y - 15, text=f"({agv_lat:.4f}, {agv_long:.4f})", fill="white", font=("Helvetica", 14, "bold"))

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

        mapCanvas.create_oval(survivor_x - 10, survivor_y - 10, survivor_x + 10, survivor_y + 10, fill="red", outline="white", width=2)

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
batteryLevel = 100
def updateBatteryLevel():
    global batteryLevel
    if batteryLevel > 0:
        batteryLevel -= 1
    batteryProgressBar['value'] = batteryLevel
    batteryLabel.config(text=f'Battery: {batteryLevel}%')
    if batteryLevel <= 10:
        batteryProgressBar.configure(bootstyle="danger")
    elif batteryLevel < 50:
        batteryProgressBar.configure(bootstyle="warning")
    else:
        batteryProgressBar.configure(bootstyle="info")
    batteryProgressBar['value'] = batteryLevel

    #update every 2 minutes
    root.after(240000, updateBatteryLevel)

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
speech_active = False
def recognize_speech():
    global speech_active
    speech_active = True
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        print("Listening.")
        try:
            audio = recognizer.listen(source)
            vocalValue = recognizer.recognize_google(audio)
            root.after(0, lambda: vocalDataEntry.delete(0, tk.END))
            root.after(0, lambda: vocalDataEntry.insert(0, vocalValue))

            addNotification("Voice detected")
                
        except sr.UnknownValueError:
            vocalValue = ""
        except sr.RequestError:
            vocalValue = "API error"
    speech_active = False

def updateVocalData():
    threading.Thread(target=recognize_speech, daemon=True).start()

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
        send_command_to_server("forward")
        addNotification("AGV Forward Movement")
        root.after(100,forward)
def backward():
    if button_pressed:
        # MotorControl.move_reverse(duration=2)
        send_command_to_server("backward")
        addNotification("AGV Backward Movement")
        root.after(100,backward)
def left():
    if button_pressed:
        # MotorControl.turn_left(duration=2)
        send_command_to_server("left")
        addNotification("AGV Left Movement")
        root.after(100,left)
def right():
    if button_pressed:
        # MotorControlß.turn_right(duration=2)
        send_command_to_server("right")
        addNotification("AGV Right Movement")
        root.after(100,right)
def stop():
    if button_pressed:
        #MotorControl.stop()
        send_command_to_server("stop")
        addNotification("AGV Stop")

def on_press(direction):
    global button_pressed
    button_pressed = True
    direction()

def on_release():
    global button_pressed
    button_pressed = False
    stop()


# def cameraFeed():
#     global imgTk
#     ret, frame = camera.read()
#     if ret:
#         label_width = cameraLabel.winfo_width()
#         label_height = cameraLabel.winfo_height()

#         if label_width > 1 and label_height > 1:
#             frame_height, frame_width = frame.shape[:2]
#             aspect_ratio = frame_width / frame_height

#             if label_width / aspect_ratio <= label_height:
#                 new_width = label_width
#                 new_height = int(label_width / aspect_ratio)
#             else:
#                 new_height = label_height
#                 new_width = int(label_height * aspect_ratio)

#             frame = cv2.resize(frame, (new_width, new_height))

#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         img = Image.fromarray(frame)
#         imgTk = ImageTk.PhotoImage(image=img)
#         cameraLabel.imgTk = imgTk
#         cameraLabel.config(image=imgTk)

#     cameraLabel.after(10, cameraFeed)

def receive_camera_feed(camera_socket, camera_label):
    data = b""
    payload_size = struct.calcsize("Q")

    def update_frame():
        nonlocal data
        try:
            while len(data) < payload_size:
                packet = camera_socket.recv(4096)
                if not packet:
                    print("Disconnected from camera server.")
                    return
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                packet = camera_socket.recv(4096)
                if not packet:
                    print("Disconnected from camera server.")
                    return
                data += packet

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgTk = ImageTk.PhotoImage(image=img)

            camera_label.imgTk = imgTk  # Prevent garbage collection
            camera_label.config(image=imgTk)
        except Exception as e:
            print(f"Camera stream error: {e}")
            return

        camera_label.after(10, update_frame)

    update_frame()

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
    global lat, long, collectDataButton
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
            row_count = len(dataTable.get_children())
            tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'
            dataTable.insert('', 'end', values=(location, currentTime, heartbeat, vocal, bodyTemp), tags=(tag,))

        except Exception as e:
            print(f"Error: {e}")
            addNotification(f"Error: {e}",f"Error: {e}")

        shortMessage = "Data logged successfully"        
        fullMessage = f"Data logged successfully at {currentTime} - {heartbeat} bpm, {vocal}, {bodyTemp} °C"
        addNotification(shortMessage,fullMessage)

        collectDataButton.config(bootstyle="success")
        root.after(1000, lambda: collectDataButton.config(bootstyle="primary"))
        
    except Exception as e:
        addNotification('Error in logging data', f"Error: {str(e)}")
        collectDataButton.config(bootstyle="danger")
        root.after(1000, lambda: collectDataButton.config(bootstyle="primary"))

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
root = ttkb.Window(themename='darkly')
root.state('zoomed')
root.title('AGV-HSD')
# root.geometry('1000x600')
root.minsize(1050, 700)
root.resizable(True, True)

#tabs frame
notebook = Notebook()
notebook.pack(fill='both', expand=True)

# CREATE TABS
updatesTab = Frame(notebook, style="DarkTab.TFrame")
trackingTab = Frame(notebook, style="DarkTab.TFrame")
survivorTab = Frame(notebook, style="DarkTab.TFrame")
pathTab = Frame(notebook, style="DarkTab.TFrame")
thermalCamTab = Frame(notebook, style="DarkTab.TFrame")

#add tabs to notebook
notebook.add(updatesTab, text='AGV Status Updates')
notebook.add(trackingTab, text='Real-Time AGV Tracking')
notebook.add(thermalCamTab, text='Thermal Camera')
notebook.add(survivorTab, text='Real-Time Survivor Detection Status')
notebook.add(pathTab, text='AGV Path')

#Global Styling
style = Style()
style.configure("DarkTab.TFrame", background="black")

style.configure("TNotebook.Tab", 
    font=("Segoe UI", 15, "bold"),
    padding=[12, 6],
    background="#222222",
    foreground="white"      
)
style.map("TNotebook.Tab",
    foreground=[
        ("selected", "white"),
        ("!selected", "#a0a0a0")],
        background=[
        ("selected", "#0a4a74"),
        ("!selected", "#2f323b")]
)
style.configure("Custom.TEntry",
    fieldbackground="#2f2f2f",
    foreground="white",
    bordercolor="#395d84",
    lightcolor="#395d84", 
    darkcolor="#395d84",  
    borderwidth=0.2,
    relief="solid",
    padding=5,
    font=("Segoe UI", 11)
)

#label styling
style.configure(
    "TLabel",
    background="#444444",
    foreground="white",
    font=('Segoe UI', 12))
#frame styling
style.configure(
    "TFrame",
    background="#145a8d")

#clock label
clockLabel = Label(root, text='', font=('Helvetica', 18), bootstyle="light")
clockLabel.place(relx=1.0, rely=0.0, anchor='ne', x=-20, y=5)
updateclock()

#AGV STATUS UPDATES TAB
#left frame
#notification bar with scroll bar in left panel
leftFrame = Frame(updatesTab, padding=10, bootstyle="dark")
leftFrame.grid(row=0, column=0, sticky='nsew')
leftFrame.grid_propagate(False)

notificationsLabel = Label(
    leftFrame,
    text='Notifications',
    width=20,
    font=('Helvetica', 18, 'bold'),
    background='#303031')
notificationsLabel.pack(pady=(10, 5), anchor='w')

scrollbar = Scrollbar(leftFrame, orient=VERTICAL, bootstyle="secondary-round")
scrollbar.pack(side=RIGHT, fill=Y)

#list of notifications in leftFrame
notificationList = Listbox(
    leftFrame,
    yscrollcommand=scrollbar.set,
    width=30,
    height=15,
    bg='#f8f8f2',
    fg='black',
    font=('Consolas', 14),
    bd=0,
    highlightthickness=1,
    highlightbackground='#444',
    selectbackground='#cce5ff',
    selectforeground='black',
    relief=FLAT )
notificationList.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=notificationList.yview)

#right frame
#data section
rightFrame = Frame(updatesTab, padding=10, bootstyle="dark")
rightFrame.grid(row=0, column=1, sticky='nsew', pady=(40,0))

heartbeatFrame = Frame(rightFrame, padding=20, bootstyle="secondary")
heartbeatFrame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

heartbeatLabel = Label(
    heartbeatFrame,
    text=' Heartbeat Data',
    font=('Segoe UI', 18, 'bold'))
heartbeatLabel.grid(row=1, column=0, padx=5, pady=(10, 0), sticky='sw')

heartbeatDataEntry = Entry(
    heartbeatFrame,
    width=25,
    font=('Segoe UI', 16),
    style="Custom.TEntry")
heartbeatDataEntry.grid(row=2, column=0, padx=10, pady=(0, 5), sticky='n')

updateHeartbeatData()

#vocal data
vocalFrame = Frame(rightFrame, padding=20, bootstyle="secondary")
vocalFrame.grid(row=3, column=0, padx=10, pady=10, sticky='ew')

vocalLabel = Label(
    vocalFrame,
    text=' Vocal Response',
    font=('Segoe UI', 18, 'bold'))
vocalLabel.grid(row=0, column=0, padx=5, pady=(10, 0), sticky='sw')

sendVocalsButton = Button(
    vocalFrame,
    text="Send Vocal Data",
    command=playVocalSound,
    bootstyle="primary" )
sendVocalsButton.grid(row=2, column=1, padx=(5,10), pady=0, sticky='e')

vocalDataEntry = Entry(
    vocalFrame,
    width=25,
    font=('Segoe UI', 16),
    style="Custom.TEntry")
vocalDataEntry.grid(row=2, column=0, padx=(10,5), pady=5, sticky='nesw')

#microphone buttons
play_icon = tk.PhotoImage(file=project_root/"GUI/play_icon.png")
pause_icon = tk.PhotoImage(file=project_root/"GUI/pause_icon.png")

def play():
    global speech_active
    stop_audio_stream()
    speech_active = True
    threading.Thread(target=recognize_speech, daemon=True).start()

# Pause Button - Resume Waveform
def pause():
    global speech_active
    speech_active = False
    start_audio_stream()
    audio_queue.queue.clear()
    root.after(100, updateWaveform)

play_button = Button(
    vocalFrame,
    image=play_icon,
    command=play,
    bootstyle='secondary')
play_button.image = play_icon
play_button.grid(row=3, column=0, padx=5, pady=0, sticky='nw')

pause_button = Button(
    vocalFrame,
    image=pause_icon,
    command=pause,
    bootstyle="secondary")
pause_button.image = pause_icon
pause_button.grid(row=3, column=0, padx=(60, 0), pady=0, sticky='nw')

#waveform
waveformFrame = Frame(rightFrame, padding=20, bootstyle="secondary")
waveformFrame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

waveFormLabel = Label(
    waveformFrame,
    text='Vocal Waves',
    font=('Segoe UI', 18, 'bold')
)
waveFormLabel.grid(row=0, column=0, padx=5, pady=5, sticky='w')

fig = Figure(figsize=(3.5, 0.75), dpi=100, facecolor="white")
ax = fig.add_subplot(111)
ax.set_facecolor("white")
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks([])
ax.set_yticks([])
ax.tick_params(left=False, bottom=False)
ax.set_ylim(-1.3, 1.3)
ax.set_xlim(-8, 108)
line, = ax.plot(np.arange(100), y_data, lw=2, color="#3597d8") 

canvas = FigureCanvasTkAgg(fig, master=waveformFrame)
canvas.get_tk_widget().grid(row=1, column=0, padx=5, pady=5, sticky='ew')

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio Status: {status}")
        addNotification(f"Audio Status: {status}",f"Audio Status: {status}")
    
    audio_data = indata[:,0]
    audio_queue.put(audio_data)
    # print(f"Audio Data Shape: {indata.shape}")

def updateWaveform():
    global y_data
    if speech_active:
        y_data = np.zeros(100)

    elif not audio_queue.empty():
        audio_data = audio_queue.get()
        audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data

        # Clip or pad data to exactly 100 samples
        y_data = np.pad(audio_data, (0, max(0, 100 - len(audio_data))), mode='constant')[:100]
    else:
        y_data = np.zeros(100)
    
    line.set_ydata(y_data)
    canvas.draw()
    
    if not speech_active:
        root.after(50, updateWaveform)

def start_audio_stream():
    global stream
    try:
        if stream is not None:
            stream.stop()
            stream.close()

        stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=44100, blocksize=100)
        stream.start()
        print("Audio stream started")
        addNotification("Audio stream started","Audio stream started")
    except Exception as e:
        print(f"Failed to stream audio: {e}")
        addNotification(f"Audio Stream Error: {e}",f"Audio Stream Error: {e}")

def stop_audio_stream():
    global stream
    if stream:
        stream.stop()
        stream.close()
        stream = None
        print("Audio stream stopped")

def start_audio_and_waveform():
    start_audio_stream()
    updateWaveform()

# Delay stream start to ensure canvas is initialized
root.after(100, start_audio_and_waveform)

# Update the thermal camera feed function
# def update_thermal_camera():
    # global thermalImgTk

    # # Get the thermal frame from the camera
    # thermal_frame = thermal_camera.get_image_frame_for_gui()
    
    # # Convert the frame to a Tkinter-compatible format
    # thermal_img = Image.fromarray(cv2.cvtColor(thermal_frame, cv2.COLOR_BGR2RGB))
    # thermal_img = thermal_img.resize((1920, 1080))  # Resize to match the label size
    # thermalImgTk = ImageTk.PhotoImage(image=thermal_img)

    # # Update the label with the new image
    # ThermalCameraLabel.imgTk = thermalImgTk
    # ThermalCameraLabel.config(image=thermalImgTk)

    # # Schedule the next update (100ms delay)
    # ThermalCameraLabel.after(100, update_thermal_camera)

#body temp data
bodytempFrame = Frame(rightFrame, padding=20, bootstyle="secondary")
bodytempFrame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

bodytempLabel = Label(
    bodytempFrame,
    text=' Body Temp °C',
    font=('Segoe UI', 18, 'bold'))
bodytempLabel.grid(row=0, column=0, padx=5, pady=(10, 0), sticky='sw')

bodytempDataEntry = Entry(
    bodytempFrame,
    width=10,
    font=('Segoe UI', 16),
    style="Custom.TEntry")
bodytempDataEntry.grid(row=1, column=0, padx=10, pady=(0, 5), sticky='wn')

updateBodyTempData()

#agv location data
locationFrame = Frame(rightFrame, padding=20, bootstyle="secondary")
locationFrame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

locationLabel = Label(
    locationFrame,
    text='AGV Location',
    font=('Segoe UI', 18, 'bold'))
locationLabel.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='w')

locationDataEntry = Entry(
    locationFrame,
    width=50,
    font=('Segoe UI', 16),
    style="Custom.TEntry")
locationDataEntry.grid(row=1, column=0, padx=10, pady=(0, 5), sticky='n')

#agv manual movement arrows
movementFrame = Frame(rightFrame, padding=20, bootstyle="secondary")
movementFrame.grid(row=2, column=1, rowspan=2, padx=10, pady=10, sticky='nsew')

centerFrame = Frame(movementFrame, bootstyle="secondary")
centerFrame.grid(row=0, column=0, sticky='nsew', pady=(0,20))

movementLabel = Label(
    centerFrame,
    text='Manual AGV Control',
    font=('Segoe UI', 18, 'bold'))
movementLabel.grid(row=0, column=0, padx=0, pady=(30, 10), sticky='n')

arrowFrame = Frame(centerFrame, bootstyle="secondary")
arrowFrame.grid(row=1, column=0, sticky='n')

arrow_btn_config = {
    "bootstyle": "info-lg",
    "padding": (20, 15),
    "width": 10,
    "style": "Large.TButton"}

forwardButton = Button(arrowFrame, text='Forward', **arrow_btn_config)
forwardButton.grid(row=0, column=1, padx=10, pady=10)
forwardButton.bind("<ButtonPress>", lambda event: on_press(forward))
forwardButton.bind("<ButtonRelease>", lambda event: on_release())

backwardButton = Button(arrowFrame, text='Backward', **arrow_btn_config)
backwardButton.grid(row=2, column=1, padx=10, pady=10)
backwardButton.bind("<ButtonPress>", lambda event: on_press(backward))
backwardButton.bind("<ButtonRelease>", lambda event: on_release())

leftButton = Button(arrowFrame, text='Left', **arrow_btn_config)
leftButton.grid(row=1, column=0, padx=10, pady=10)
leftButton.bind("<ButtonPress>", lambda event: on_press(left))
leftButton.bind("<ButtonRelease>", lambda event: on_release())

rightButton = Button(arrowFrame, text='Right', **arrow_btn_config)
rightButton.grid(row=1, column=2, padx=10, pady=10)
rightButton.bind("<ButtonPress>", lambda event: on_press(right))
rightButton.bind("<ButtonRelease>", lambda event: on_release())

stopButton = Button(arrowFrame, text='Stop', **arrow_btn_config)
stopButton.grid(row=1, column=1, padx=5, pady=5)

#mechanical arm
armFrame = Frame(rightFrame, padding=20, bootstyle="secondary")
armFrame.grid(row=0, column=1, padx=85, pady=10, sticky='nsew')

armLabel = Label(
    armFrame,
    text='Mechanical Arm Control',
    font=('Segoe UI', 18, 'bold'))
armLabel.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='nsew')

#bottom frame
#battery progress bar
style.configure("NoBorder.TFrame",
    background="#222222",
    borderwidth=0,
    relief="flat")

style.configure("FlatBattery.Horizontal.TProgressbar",
    background="#4f94d4",
    troughcolor="white",
    bordercolor="#222222",
    lightcolor="#222222",
    darkcolor="#222222")

bottomFrame = Frame(updatesTab, padding=10, style="NoBorder.TFrame")
bottomFrame.grid(row=2, column=0, columnspan=2, sticky='ew')

batteryLabel = Label(
    bottomFrame,
    text='Battery: 0%',
    font=('Segoe UI', 12),
    background="#222222",
    foreground="white")
batteryLabel.grid(row=0, column=0, padx=(0, 10), sticky='w')

batteryProgressBar = ttkb.Progressbar(
    bottomFrame,
    orient='horizontal',
    length=200,
    mode='determinate',
    style="FlatBattery.Horizontal.TProgressbar")
batteryProgressBar.grid(row=0, column=1, padx=(0, 10), sticky='w')

updateBatteryLevel()

#data log button
style.configure("LogData.TButton", font=("Segoe UI", 14, "bold"))
collectDataButton = Button(
    bottomFrame,
    text="Log Data",
    command=logSensorData,
    style='LogData.TButton',
    padding=(15, 10))
collectDataButton.grid(row=0, column=2, padx=(10, 0), sticky='e')

#AGV REAL-TIME UPDATES TAB
#camera frame
CAMERA_WIDTH=450
CAMERA_HEIGHT=300

cameraFrame = Frame(trackingTab, padding=10, bootstyle="secondary")
cameraFrame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

cameraTextLabel = Label(
    cameraFrame,
    text='AGV Camera',
    font=("Segoe UI", 16, "bold"))
cameraTextLabel.grid(row=0, column=0, sticky='w', pady=(0, 5))

cameraLabel = tk.Label(
    cameraFrame,
    text='Camera',
    background='black',
    foreground='white',
    width=CAMERA_WIDTH,
    height=CAMERA_HEIGHT)
cameraLabel.grid(row=1, column=0, sticky='nsew')

# Remove this line, since camera is now on the server:
# camera = cv2.VideoCapture(0)

# Connect to the server's camera stream
try:
    camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    camera_socket.connect(("10.33.228.31", 6000))
    print("Connected to camera feed.")
    
except Exception as e:
    print(f"Failed to connect to camera feed: {e}")
    camera_socket = None
    
receive_camera_feed(camera_socket, cameraLabel)

#map frame
mapFrame = Frame(trackingTab, padding=10, bootstyle="secondary")
mapFrame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

AGVTextLabel = Label(
    mapFrame,
    text='AGV Environment Map',
    font=("Segoe UI", 16, "bold"))
AGVTextLabel.grid(row=0, column=0, sticky='w', pady=(0, 5))

mapCanvas = Canvas(
    mapFrame,
    bg='black',
    width=500,
    height=CAMERA_HEIGHT)
mapCanvas.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))

trackingMap()

#SURVIVOR DETECTION TAB
#table
tableFrame = Frame(survivorTab, padding=10, bootstyle="secondary")
tableFrame.pack(fill='both', expand=True, padx=10, pady=(10, 0))
style.configure("Custom.Treeview",
    background="#444344",
    fieldbackground="#375a7f",
    foreground="white",
    rowheight=28,
    borderwidth=0)
style.configure("Custom.Treeview.Heading",
    background=style.colors.primary,
    foreground="white",
    font=("Segoe UI", 14, "bold"),
    relief="solid")
style.map("Custom.Treeview.Heading",
    background=[('active', style.colors.primary)],
    relief=[('pressed', 'flat')])

dataTable = Treeview(
    tableFrame,
    columns=('Location', 'Time', 'Heartbeat', 'Vocal', 'Body Temp °C'),
    show='headings',
    style="Custom.Treeview")

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

#bottom frame in survivor detection tab
bottomBar = Frame(survivorTab, padding=10, style='NoBorder.TFrame')
bottomBar.pack(fill='x', side='bottom')

exportButton = Button(
    bottomBar,
    text='Export Data',
    command=exportData,
    style='LogData.TButton',
    padding=(15, 10))
exportButton.pack(padx=10)

#AGV PATH TAB
pathContainer = Frame(pathTab, padding=40, bootstyle="secondary")
pathContainer.grid(row=0, column=0, sticky='nsew')

# Make sure pathTab expands properly
pathTab.grid_rowconfigure(0, weight=1)
pathTab.grid_columnconfigure(0, weight=1)

# Let pathContainer expand its rows (adjust weights as needed)
for i in range(12):
    pathContainer.grid_rowconfigure(i, weight=1)
pathContainer.grid_columnconfigure(0, weight=1)

# Fonts and settings
LABEL_FONT = ("Segoe UI", 16, "bold")
ENTRY_FONT = ("Segoe UI", 14)

# Title
pathLabel = Label(
    pathContainer,
    text='AGV Point A to Point B',
    font=("Segoe UI", 20, "bold"))
pathLabel.grid(row=0, column=0, pady=0, sticky='n')

# Current location
pointALabel = Label(pathContainer, text='Current Location (latitude, longitude)', font=LABEL_FONT)
pointALabel.grid(row=1, column=0, pady=(10, 0), sticky='w')
pointAEntry = Entry(pathContainer, font=ENTRY_FONT)
pointAEntry.grid(row=2, column=0, pady=(20, 5), sticky='ew')

# Destination
pointBLabel = Label(pathContainer, text='Enter Destination (latitude, longitude)', font=LABEL_FONT)
pointBLabel.grid(row=3, column=0, pady=(10, 0), sticky='w')
pointBEntry = Entry(pathContainer, font=ENTRY_FONT)
pointBEntry.grid(row=4, column=0, pady=(0, 5), sticky='ew')

# Distance
distanceLabel = Label(pathContainer, text='Resulting Distance in kilometers', font=LABEL_FONT)
distanceLabel.grid(row=5, column=0, pady=(10, 0), sticky='w')
distanceDisplay = Entry(pathContainer, font=ENTRY_FONT)
distanceDisplay.grid(row=6, column=0, pady=(0, 5), sticky='ew')

# Direction
directionLabel = Label(pathContainer, text='Resulting Direction Clockwise From North (degrees)', font=LABEL_FONT)
directionLabel.grid(row=7, column=0, pady=(10, 0), sticky='w')
directionDisplay = Entry(pathContainer, font=ENTRY_FONT)
directionDisplay.grid(row=8, column=0, pady=(0, 5), sticky='ew')

#Calculate Direction And Distance
# Calculation logic
def calculateVector():
    try:
        pointA = pointAEntry.get().split(',')
        pointB = pointBEntry.get().split(',')

        if len(pointA) != 2 or len(pointB) != 2:
            raise ValueError("Invalid input format. Use (latitude, longitude)")

        latA, longA = map(float, pointA)
        latB, longB = map(float, pointB)

        # Haversine formula
        R = 6371  # Earth radius in km
        dlat = np.radians(latB - latA)
        dlong = np.radians(longB - longA)
        a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(latA)) * np.cos(np.radians(latB)) * np.sin(dlong / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = R * c

        y = np.sin(dlong) * np.cos(np.radians(latB))
        x = np.cos(np.radians(latA)) * np.sin(np.radians(latB)) - np.sin(np.radians(latA)) * np.cos(np.radians(latB)) * np.cos(dlong)
        direction = (np.degrees(np.arctan2(y, x)) + 360) % 360

        distanceDisplay.delete(0, END)
        distanceDisplay.insert(0, f"{distance:.4f}")
        directionDisplay.delete(0, END)
        directionDisplay.insert(0, f"{direction:.2f}")
    except Exception as e:
        distanceDisplay.delete(0, END)
        distanceDisplay.insert(0, f"Error: {str(e)}")
        directionDisplay.delete(0, END)
        directionDisplay.insert(0, "")

# Calculate button
calculateDistanceDirection = Button(
    pathContainer,
    text="Get Distance & Direction",
    command=calculateVector,
    style='LogData.TButton')
calculateDistanceDirection.grid(row=9, column=0, pady=(15, 0), sticky='n')

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

# #for window scaling
updatesTab.grid_rowconfigure(0, weight=1)
updatesTab.grid_columnconfigure(1, weight=1)

vocalFrame.grid_columnconfigure(0, weight=1)
vocalFrame.grid_columnconfigure(1, weight=0)

waveformFrame.grid_columnconfigure(0, weight=1)
canvas.get_tk_widget().grid(row=1, column=0, padx=0, pady=0, sticky='nsew')
waveformFrame.grid_columnconfigure(0, weight=1)
waveformFrame.grid_rowconfigure(1, weight=1)
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

movementFrame.grid_rowconfigure(0, weight=1)
movementFrame.grid_columnconfigure(0, weight=1)
centerFrame.grid_rowconfigure(0, weight=1)
centerFrame.grid_columnconfigure(0, weight=1)

arrowFrame.grid_columnconfigure(0, weight=1)
arrowFrame.grid_columnconfigure(1, weight=1)
arrowFrame.grid_columnconfigure(2, weight=1)

bottomFrame.grid_columnconfigure(2, weight=1)

trackingTab.grid_rowconfigure(0, weight=1)
trackingTab.grid_columnconfigure(0, weight=1)
trackingTab.grid_columnconfigure(1, weight=1)

cameraFrame.grid_rowconfigure(1, weight=1)
cameraFrame.grid_columnconfigure(0, weight=1)

mapFrame.grid_rowconfigure(1, weight=1)
mapFrame.grid_columnconfigure(0, weight=1)

dataTable.tag_configure('oddrow', background='#444344')
dataTable.tag_configure('evenrow', background='#3c3c3c')

# trackingTab.columnconfigure(0, weight=1)
# trackingTab.columnconfigure(1, weight=2)
# trackingTab.rowconfigure(0,weight=1)

# mapFrame.grid_rowconfigure(0, weight=0)
# mapFrame.grid_rowconfigure(1, weight=1)
# mapFrame.grid_columnconfigure(0, weight=1)

# trackingTab.grid_rowconfigure(0, weight=1)
# trackingTab.grid_rowconfigure(1, weight=1)
# trackingTab.grid_columnconfigure(0, weight=1)
# trackingTab.grid_columnconfigure(1, weight=1)


# #thermal camera frame
# ThermalCameraFrame = ttk.Frame(thermalCamTab, width=10, height=10)
# ThermalCameraFrame.grid(row=1, column=0, padx=0, pady=10, sticky='news')
# ThermalCameraLabel = ttk.Label(thermalCamTab)
# ThermalCameraLabel.grid(row=0, column=0, padx=10, pady=10)

# # Start the thermal camera feed when the application runs
# # update_thermal_camera()

def main():
    root.mainloop()

if __name__ == "__main__":
    main()

