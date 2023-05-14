 # Import required libraries
import cv2 as cv
import torch
import numpy as np
import urllib.request
from gpiozero import LED
import RPi.GPIO as GPIO
import time
import subprocess

class setUp:
    def __init__(self):
       
        self.model = None
        self.imgResponse = None

       
        # Set a default state of the two modes
        self.state = False
        # Set a default image number
        self.image_count = 0
        # Set a default trigger state
        self.state_automat = 0

        # Define some constants for pin numbers
        self.AUTOMAT_PIN = 33
        self.BUTTON_PIN = 22
        self.READY_PIN = 17
        self.RESULT_READY_PIN = 35
        self.CORRECT_PIN = 18
        self.DEFECTIVE1_PIN = 27
        self.DEFECTIVE2_PIN = 22
        self.DEFECTIVE3_PIN = 24

        # Set up the GPIO pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.RESULT_READY_PIN, GPIO.OUT)
        GPIO.setup(self.AUTOMAT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Set up the leds' pins
        self.led_ready = LED(self.READY_PIN)
        self.led_correct = LED(self.CORRECT_PIN)
        self.led_defective1 = LED(self.DEFECTIVE1_PIN)
        self.led_defective2 = LED(self.DEFECTIVE2_PIN)
        self.led_defective3 = LED(self.DEFECTIVE3_PIN)

        # Turn off the LEDs
        self.led_ready.off()
        self.led_correct.off()
        self.led_defective1.off()
        self.led_defective2.off()
        self.led_defective3.off()

        # Load the custom-trained computer vision model
        self.model = torch.hub.load('.', 'custom', path='bestV2.pt', source='local')
        # Define the confidence for the model
        self.model.conf = 0.85

        # Set up an interrupt for the button
        GPIO.add_event_detect(self.BUTTON_PIN, GPIO.BOTH, callback=self.change_state, bouncetime=500)
        GPIO.add_event_detect(self.AUTOMAT_PIN, GPIO.RISING, callback=self.change_image_count, bouncetime=500)

    def change_state(self, BUTTON_PIN):
        self.state = not self.state

    def change_image_count(self, AUTOMAT_PIN):
        self.image_count = 1
        self.state_automat = 1

    def control_temperature(self):
        temperature_c = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
        temperature_c = float(temperature_c.replace("temp=", "").replace("'C\n", ""))
        print("Temperature: {:.2f}°C".format(temperature_c))

    def check_connection(self):
        connected = False
        while not connected:
            try:
                self.imgResponse = urllib.request.urlopen("http://192.168.43.117/capture?", timeout=5)
                self.control_led('1')
                connected = True
            except:
                self.control_led("111")

    def predict(self):
        imgNp = np.array(bytearray(self.imgResponse.read()), dtype=np.uint8)
        frame = cv.imdecode(imgNp, -1)
        return frame, self.model(frame)

    def control_led(self, state_code):
        # (000: normal / 001: nothing / 011: reversed on x axis / 100: left / 101: tilted_right / 110: tilted_left)
        if state_code == "000":
            print("Normal")
        elif state_code == "001":
            print("Nothing")
        elif state_code == "011":
            print("Inverted")
        elif state_code == "100":
            print("Left")
        elif state_code == "101":
            print("Font wrong")
        elif state_code == "110":
            print("Logo is under")
        elif state_code == "111":
            print("Failed...")
        elif state_code == "1":
            print("Done")
        else:
            print("Invalid state code")

    def show_result(self, result, width):
        bbox_height_part = None
        bbox_height_normal = None
        if result.pandas().xyxy[0].empty:
            self.control_led("001")
        else:
            for index, row in result.pandas().xyxy[0].iterrows():
                xmin, ymin, xmax, ymax = row[0], row[1], row[2], row[3]
                center_x = (xmin + xmax) / 2
                if center_x < width / 2:
                    self.control_led("100")
                if row[6] == "part":
                    x1, y1, x2, y2 = row[:4].astype(int)
                    bbox_height_part = y2 - y1
                elif row[6] == "Normal":
                    x1, y1n, x2, y2n = row[:4].astype(int)
                    bbox_height_normal = y2n - y1n
                if bbox_height_part and bbox_height_normal:
                    ratio_position = bbox_height_part / bbox_height_normal
                    ratio_word = (y1 - y1n) * 100 // (y2n - y1n)
                    bbox_height_part = None
                    bbox_height_normal = None
                    if ratio_word > 40:
                        self.control_led("101")
                    if ratio_word > 0.51:
                        self.control_led("110")
                else:
                    if row[6] == "Normal":
                        self.control_led("000")
                    if row[6] == "Inverted":
                        self.control_led("011")

    def continues_mode(self):
        self.check_connection()
        frame, result = self.predict()
        height, width, _ = frame.shape
        self.show_result(result, width)
        

    def optimal_mode(self):
        self.check_connection()
        frame, result = self.predict()
        height, width, _ = frame.shape
        self.show_result(result, width)
        GPIO.output(self.RESULT_READY_PIN, 1)
        state_ready = GPIO.input(self.RESULT_READY_PIN)
        print("State of GPIO pin 35: {}".format(state_ready))
        time.sleep(0.25)
        GPIO.output(self.RESULT_READY_PIN, 0)
        state_ready = GPIO.input(self.RESULT_READY_PIN)
        print("State of GPIO pin 35: {}".format(state_ready))
        return 0 , 0