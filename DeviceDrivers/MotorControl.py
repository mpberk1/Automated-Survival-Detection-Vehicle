import RPi.GPIO as GPIO
import time

# Assign a single GPIO pin to control both motors
MOTORS_CTRL = 17  # Change this to the GPIO pin you are using

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTORS_CTRL, GPIO.OUT)

def forward():
    print("Moving forward")
    GPIO.output(MOTORS_CTRL, GPIO.HIGH)  # Motors move forward

def backward():
    print("Moving backward")
    GPIO.output(MOTORS_CTRL, GPIO.LOW)  # Motors move backward

def stop():
    print("Stopping")
    GPIO.output(MOTORS_CTRL, GPIO.LOW)  # Stop (assuming LOW stops motion)

def motor_control():
    try:
        while True:
            forward()
            print("Moving forward for 2 seconds")
            time.sleep(2)

            stop()
            time.sleep(1)

            backward()
            print("Moving backward for 2 seconds")
            time.sleep(2)

            stop()
            print("Waiting 5 seconds")
            time.sleep(5)

    except KeyboardInterrupt:
        print("Program interrupted by user")

    finally:
        stop()
        GPIO.cleanup()

if __name__ == "__main__":
    motor_control()
