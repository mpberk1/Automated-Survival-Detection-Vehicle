import serial
import time

# Constants similar to Arduino code
FULL_FORWARD_M1 = 127
FULL_FORWARD_M2 = 255
STOP_M1 = 64
STOP_M2 = 192
REVERSE_M1 = 1
REVERSE_M2 = 128

# Serial setup
ser = serial.Serial('/dev/serial0', 38400, timeout=1)  # Open the serial port

def forward():
    # Full forward for Motor 1
    print("Motor 1 forward")
    ser.write(bytes([FULL_FORWARD_M1]))
            
    # Full forward for Motor 2
    print("Motor 2 forward")
    ser.write(bytes([FULL_FORWARD_M2])) 

def backward():
     # Reverse Motor 1
    print("Motor 1 reverse")
    ser.write(bytes([REVERSE_M1]))
            
    # Reverse Motor 2
    print("Motor 2 reverse")
    ser.write(bytes([REVERSE_M2]))

def left():
    # Stop Motor 1
    print("Motor 1 stop")
    ser.write(bytes([STOP_M1]))
    
    # Full forward for Motor 2
    print("Motor 2 forward")
    ser.write(bytes([FULL_FORWARD_M2])) 

def right():
    # Stop Motor 2
    print("Motor 2 stop")
    ser.write(bytes([STOP_M2]))

    # Full forward for Motor 1
    print("Motor 1 forward")
    ser.write(bytes([FULL_FORWARD_M1]))

def stop():
    # Stop Motor 1
    print("Motor 1 stop")
    ser.write(bytes([STOP_M1]))
            
    # Stop Motor 2
    print("Motor 2 stop")
    ser.write(bytes([STOP_M2]))

def motor_control():
    try:
        while True:
            
            forward()
            # Delay for 2 seconds
            print("Delay 2 seconds")
            time.sleep(2)
            
            stop()

            backward()
            
            # End of loop, delay for 5 seconds
            print("End of loop; delay 5 seconds")
            time.sleep(5)

    except KeyboardInterrupt:
        print("Program interrupted by user")
    
    finally:
        ser.close()  # Close serial port when done

if __name__ == "__main__":
    motor_control()
