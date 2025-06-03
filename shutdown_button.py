import RPi.GPIO as GPIO
import time
import os
import signal
import sys

BUTTON_GPIO = 23  # GPIO23 = pin 16

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def init_gpio():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    init_gpio()
    
    try:
        while True:
            if GPIO.input(BUTTON_GPIO) == GPIO.LOW:
                print("Shutdown button pressed!")
                os.system("sudo shutdown -h now")
                break
            time.sleep(0.2)
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        GPIO.cleanup()