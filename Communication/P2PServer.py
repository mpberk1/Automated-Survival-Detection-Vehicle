import socket
import importlib.util
import sys
import os
from pathlib import Path

# Dynamically get file paths
current_file = Path(__file__)  # Path to this file
project_root = current_file.parent.parent  # Path to Automated-Survival-Detection-Vehicle
sys.path.insert(0, str(project_root))
# Path to MotorControl.py
motor_path = project_root / "DeviceDrivers" / "MotorControl.py"

# Load MotorControl module
spec = importlib.util.spec_from_file_location("MotorControl", motor_path)
motor = importlib.util.module_from_spec(spec)
sys.modules["MotorControl"] = motor
spec.loader.exec_module(motor)

# Command dispatcher
def handle_command(command):
    #forward
    if command == "forward":
        result = motor.move_forward()
        return result if result is not None else "Executed: forward"
    #backward
    elif command == "backward":
        result = motor.move_reverse()
        return result if result is not None else "Executed: backward"
    #left
    elif command == "left":
        result = motor.turn_left()
        return result if result is not None else "Executed: turn left"
    #right
    elif command == "right":
        result = motor.turn_right()
        return result if result is not None else "Executed: turn right"
    #stop
    elif command == "stop":
        result = motor.stop()
        return result if result is not None else "Executed: stop"
    else:
        return f"Unknown command: {command}"

# Server function using static IP
def p2p_server(host="10.33.253.71", port=5000):  # <== STATIC IP HERE
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    while True:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            break
        print(f"Received: {data}")

        response = handle_command(data)
        conn.sendall(response.encode('utf-8'))

    conn.close()
    server_socket.close()

if __name__ == "__main__":
    p2p_server()
