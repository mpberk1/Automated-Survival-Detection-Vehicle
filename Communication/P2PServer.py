import socket
import importlib.util
import sys
import os
from pathlib import Path
import cv2
import pickle
import struct
import threading

# Dynamically get file paths
current_file = Path(__file__)  # Path to this file
project_root = current_file.parent.parent  # Path to Automated-Survival-Detection-Vehicle
sys.path.insert(0, str(project_root))
motor_path = project_root / "DeviceDrivers" / "MotorControl.py"
sound_path = project_root / "Sound" / "soundDriver.py"

# Load MotorControl module
spec = importlib.util.spec_from_file_location("MotorControl", motor_path)
motor = importlib.util.module_from_spec(spec)
sys.modules["MotorControl"] = motor
spec.loader.exec_module(motor)

spec1 = importlib.util.spec_from_file_location("soundDriver", sound_path)
speaker = importlib.util.module_from_spec(spec1)
sys.modules["soundDriver"] = speaker
spec1.loader.exec_module(speaker)

# Command dispatcher
def handle_command(command):
    if command == "forward":
        result = motor.move_forward()
        return result if result is not None else "Executed: forward"
    elif command == "backward":
        result = motor.move_reverse()
        return result if result is not None else "Executed: backward"
    elif command == "left":
        result = motor.turn_left()
        return result if result is not None else "Executed: turn left"
    elif command == "right":
        result = motor.turn_right()
        return result if result is not None else "Executed: turn right"
    elif command == "stop":
        result = motor.stop()
        return result if result is not None else "Executed: stop"
    elif command == "play":
        result = speaker.play_sound()
        return result if result is not None else "Executed: play sound"
    else:
        return f"Unknown command: {command}"

# Handle a single client connection
def handle_client_connection(conn, addr):
    try:
        print(f"Connection established with {addr}")
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"Received from {addr}: {data}")
            response = handle_command(data)
            conn.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"Connection error with {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection with {addr} closed.")

# Server that stays open for new connections
def p2p_server(host="10.33.228.31", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[P2P Server] Listening on {host}:{port}...")

    while True:
        try:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client_connection, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[P2P Server] Accept error: {e}")

    server_socket.close()
    print("[P2P Server] Shutdown.")

# Camera streaming server
def camera_stream_server(host="10.33.228.31", port=6000):
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Camera could not be opened.")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"[Camera Server] Listening for connection on {host}:{port}...")

    conn, addr = server_socket.accept()
    print(f"[Camera Server] Connected by {addr}")

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data
            conn.sendall(message)
    except Exception as e:
        print(f"[Camera Server] Error: {e}")
    finally:
        camera.release()
        conn.close()
        server_socket.close()
        print("[Camera Server] Closed.")

if __name__ == "__main__":
    threading.Thread(target=p2p_server, daemon=True).start()
    threading.Thread(target=camera_stream_server, daemon=True).start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down.")
