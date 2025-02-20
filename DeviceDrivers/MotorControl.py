import RPi.GPIO as GPIO
import time

# Define GPIO pins for Motor 1
M1_IN1 = 17  # Motor 1 Forward
M1_IN2 = 27  # Motor 1 Reverse

# Define GPIO pins for Motor 2
M2_IN1 = 22  # Motor 2 Forward
M2_IN2 = 23  # Motor 2 Reverse

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup([M1_IN1, M1_IN2, M2_IN1, M2_IN2], GPIO.OUT)

def forward():
    print("Moving Forward")
    GPIO.output(M1_IN1, GPIO.HIGH)
    GPIO.output(M1_IN2, GPIO.LOW)
    GPIO.output(M2_IN1, GPIO.HIGH)
    GPIO.output(M2_IN2, GPIO.LOW)

def backward():
    print("Moving Backward")
    GPIO.output(M1_IN1, GPIO.LOW)
    GPIO.output(M1_IN2, GPIO.HIGH)
    GPIO.output(M2_IN1, GPIO.LOW)
    GPIO.output(M2_IN2, GPIO.HIGH)

def left():
    print("Turning Left")
    GPIO.output(M1_IN1, GPIO.LOW)  # Stop M1
    GPIO.output(M1_IN2, GPIO.LOW)
    GPIO.output(M2_IN1, GPIO.HIGH) # Move M2 Forward
    GPIO.output(M2_IN2, GPIO.LOW)

def right():
    print("Turning Right")
    GPIO.output(M1_IN1, GPIO.HIGH) # Move M1 Forward
    GPIO.output(M1_IN2, GPIO.LOW)
    GPIO.output(M2_IN1, GPIO.LOW)  # Stop M2
    GPIO.output(M2_IN2, GPIO.LOW)

def stop():
    print("Stopping")
    GPIO.output(M1_IN1, GPIO.LOW)
    GPIO.output(M1_IN2, GPIO.LOW)
    GPIO.output(M2_IN1, GPIO.LOW)
    GPIO.output(M2_IN2, GPIO.LOW)

def motor_control():
    try:
        while True:
            forward()
            time.sleep(2)
            stop()
            time.sleep(1)

            backward()
            time.sleep(2)
            stop()
            time.sleep(1)

            left()
            time.sleep(1)
            stop()
            time.sleep(1)

            right()
            time.sleep(1)
            stop()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Program interrupted by user")
    
    finally:
        stop()  # Ensure motors are stopped
        GPIO.cleanup()  # Reset GPIO pins

if __name__ == "__main__":
    motor_control()
