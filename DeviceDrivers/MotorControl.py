import RPi.GPIO as GPIO
import time

# Assign a single GPIO pin per motor
MOTOR1_CTRL = 17  # Motor 1 control
MOTOR2_CTRL = 22  # Motor 2 control

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR1_CTRL, GPIO.OUT)
GPIO.setup(MOTOR2_CTRL, GPIO.OUT)

def forward():
    print("Moving forward")
    GPIO.output(MOTOR1_CTRL, GPIO.HIGH)
    GPIO.output(MOTOR2_CTRL, GPIO.HIGH)

def backward():
    print("Moving backward")
    GPIO.output(MOTOR1_CTRL, GPIO.LOW)
    GPIO.output(MOTOR2_CTRL, GPIO.LOW)

def stop():
    print("Stopping")
    GPIO.output(MOTOR1_CTRL, GPIO.LOW)
    GPIO.output(MOTOR2_CTRL, GPIO.LOW)

def left():
    print("Turning left")
    GPIO.output(MOTOR1_CTRL, GPIO.LOW)  # One motor stops or reverses
    GPIO.output(MOTOR2_CTRL, GPIO.HIGH)

def right():
    print("Turning right")
    GPIO.output(MOTOR1_CTRL, GPIO.HIGH)
    GPIO.output(MOTOR2_CTRL, GPIO.LOW)

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
