import serial
import time

# Define motor control bytes (same as Arduino)
FULL_FORWARD_M1 = 127
FULL_FORWARD_M2 = 255
STOP_M1 = 64
STOP_M2 = 192
REVERSE_M1 = 1
REVERSE_M2 = 128

# Set up serial communication on the Pi's UART (GPIO14 TX, GPIO15 RX)
ser = serial.Serial("/dev/ttyAMA0", baudrate=38400, timeout=1)

def send_command(command):
    """Send a single byte command to the motor driver."""
    ser.write(bytes([command]))
    print(f"Sent command: {command}")

def move_forward():
    """Move both motors forward for a specified duration."""
    print("Moving forward...")
    send_command(FULL_FORWARD_M1)
    send_command(FULL_FORWARD_M2)
    # stop()

def stop():
    """Stop both motors."""
    print("Stopping motors...")
    send_command(STOP_M1)
    send_command(STOP_M2)

def move_reverse():
    """Move both motors in reverse for a specified duration."""
    print("Moving in reverse...")
    send_command(REVERSE_M1)
    send_command(REVERSE_M2)
    # time.sleep(duration)
    # stop()

def turn_right():
    print("Turning Right")
    send_command(FULL_FORWARD_M1)
    send_command(STOP_M2)
    # time.sleep(duration)
    # stop()

def turn_left():
    print("Turning Left")
    send_command(FULL_FORWARD_M2)
    send_command(STOP_M1)
    # time.sleep(duration)
    # stop()

if __name__ == "__main__":
    try:
        while True:
            move_forward(2)
            time.sleep(2)
            move_reverse(5)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping program...")
        stop()
        ser.close()
