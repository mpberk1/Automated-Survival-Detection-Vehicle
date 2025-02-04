import serial
import time

# Serial Port Settings (Modify based on your system)
SERIAL_PORT = "/dev/ttyAMA0"  # Linux
BAUD_RATE = 115200
TIMEOUT = 2  # Increased timeout for better stability

# Data frame markers
MESSAGE_HEAD1 = 0x53
MESSAGE_HEAD2 = 0x59
MESSAGE_END1 = 0x54
MESSAGE_END2 = 0x43

# Human Presence Detection
HUMAN_PSE_RADAR = 0x80
SOMEONE_HERE = 0x01
NOONE_HERE = 0x00

# Movement Detection
STATIONARY = 0x01
MOVEMENT = 0x02

# Fall Detection
FALL_DETECTION = 0x83
NO_FALL = 0x00
FALL_DOWN = 0x01

# Expected Packet Size
PACKET_SIZE = 10

def read_sensor_data():
    """Reads and processes data from the fall detection sensor with enhanced debugging."""
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            print("Listening for sensor data...")

            while True:
                if ser.in_waiting > 0:
                    raw_data = ser.read(PACKET_SIZE)  # Read incoming data
                    print(f"Received raw data ({len(raw_data)} bytes): {raw_data.hex()}")  # Debugging

                    if len(raw_data) < PACKET_SIZE:
                        print("⚠️ Incomplete packet received, waiting for more data...")
                        continue

                    if is_valid_packet(raw_data):
                        process_sensor_data(raw_data)
                    else:
                        print("❌ Invalid packet received!")

                time.sleep(0.5)  # Adjust sleep time to balance CPU usage

    except serial.SerialException as e:
        print(f"⚠️ Serial Error: {e}")
    except KeyboardInterrupt:
        print("\n🔴 Stopping sensor reading.")

def is_valid_packet(data):
    """Checks if the received packet has correct start and end markers."""
    print(f"Checking packet validity: {data.hex()}")  # Debugging output

    if len(data) != PACKET_SIZE:
        print(f"❌ Invalid packet size: Expected {PACKET_SIZE}, got {len(data)}")
        return False

    if data[0] != MESSAGE_HEAD1 or data[1] != MESSAGE_HEAD2:
        print("❌ Invalid packet header!")
        return False

    if data[-2] != MESSAGE_END1 or data[-1] != MESSAGE_END2:
        print("❌ Invalid packet footer!")
        return False

    print("✅ Valid packet received!")
    return True

def process_sensor_data(data):
    """Processes the received binary data and prints relevant information."""
    try:
        print(f"Processing data: {data.hex()}")  # Debugging
        sensor_type = data[2]  # Data type identifier
        print(f"Sensor Type: {sensor_type}")

        if sensor_type == HUMAN_PSE_RADAR or SOMEONE_HERE or NOONE_HERE:
            presence_info = data[3]
            move_info = data[4]

            if presence_info == SOMEONE_HERE:
                    print("🟢 **Human detected: Someone is here**")
            if presence_info == NOONE_HERE:
                    print("🔴 **No human detected**")

            if move_info == STATIONARY:
                    print("🔵 **Person is stationary**")
            if move_info == MOVEMENT:
                    print("🟠 **Person is moving**")

            if sensor_type == FALL_DETECTION:
                fall_status = data[3]
                if fall_status == NO_FALL:
                    print("✅ **No fall detected**")
                elif fall_status == FALL_DOWN:
                    print("⚠️ **FALL DETECTED! Immediate attention needed!**")
        else:
            print(f"❓ Unknown sensor type: {sensor_type}")

    except Exception as e:
        print(f"⚠️ Data processing error: {e}")


if __name__ == "__main__":
    read_sensor_data() 