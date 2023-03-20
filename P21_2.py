import cv2 as cv
import torch
import numpy as np
import pandas as pd
import urllib.request
from gpiozero import LED
import RPi.GPIO as GPIO
import time


AUTOMAT_PIN = 33
BUTTON_PIN = 22
GPIO.setmode(GPIO.BOARD)

GPIO.setup(AUTOMAT_PIN, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_PIN, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

led_connection =LED(17)
led_correct= LED(18)
led_defective1 = LED(27)
led_defective2 = LED(22)
led_defective3 = LED(24)

led_connection.off()
led_correct.off()
led_defective1.off()
led_defective2.off()
led_defective3.off()


model = torch.hub.load('.', 'custom', path='bestV2.pt', source='local') 

model.conf = 0.85



state = False
image_count = 0

def toggle_led(BUTTON_PIN):
	global state

	state = not(state)







def continues_mode():
        while state == False:
                connected = False
                while not connected:
                    try:

                        imgResponse = urllib.request.urlopen("http://192.168.43.117/capture?",timeout = 5)
                        led_connection.on()
                        print("done")
                        connected = True
                    except:
                        led_connection.off()
                        led_correct.off()
                        led_defective1.off()
                        led_defective2.off()
                        led_defective3.off()
                        print("failed...")


                imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
                frame = cv.imdecode(imgNp,-1)
                result = model(frame)
                #get the height and the width of the frame
                height, width, _ = frame.shape

            #(001: nothing  / 011: reversed on x axis /100 : left /101: titled_right/111:tilted_left)
                if(result.pandas().xyxy[0].empty):
                    led_correct.off()
                    led_defective1.off()
                    led_defective2.off()
                    led_defective3.on()
                    print("Nothing")
                else:
                    for index,row in  result.pandas().xyxy[0].iterrows():
                        print(row[6])
                        # Define a bounding box
                        xmin, ymin, xmax, ymax = row[0], row[1],row[2],row[3]
                        # Calculate the center of the bounding box
                        center_x = (xmin + xmax) / 2
                        if(center_x < width/2):
                            led_correct.off()
                            led_defective1.on()
                            led_defective2.off()
                            led_defective3.off()

                        else:
                            if row[6] == "Normal":
                    #           print("Normal")
                                led_correct.on()
                                led_defective1.off()
                                led_defective2.off()
                                led_defective3.off()

                            if row[6] == "Inversed" :
                     #              print("Inversed")
                                led_correct.off()
                                led_defective1.off()
                                led_defective2.on()
                                led_defective3.on()
                            if row[6] == "Titled_right" :
                    #               print("Titled_right")
                                led_correct.off()
                                led_defective1.on()
                                led_defective2.off()
                                led_defective3.on()
                            if row[6] == "Titled_left":
                    #               print("Titled_right")
                                led_correct.off()
                                led_defective1.on()
                                led_defective2.on()
                                led_defective3.on()

                frame = np.squeeze(result.render())
             #   cv.imshow('FRAME',frame)
                if cv.waitKey(500)&0xFF==27:
                    break
       

def optimal_mode(image_count,state_automat):
        print("enter")
        print(state)
        print(str(image_count)+"2")
        print(str(state_automat)+"2")
        while state and image_count ==1 and state_automat ==1:
                print("here")
                print(image_count)
                print(state_automat)
                print("optimal")
                connected = False
                
                while not connected:
                    try:

                        imgResponse = urllib.request.urlopen("http://192.168.43.117/capture?",timeout = 5)
                        
                        led_connection.on()
                        print("done")
                        connected = True
                    except:
                        led_connection.off()
                        led_correct.off()
                        led_defective1.off()
                        led_defective2.off()
                        led_defective3.off()
                        print("failed...")


                imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
                frame = cv.imdecode(imgNp,-1)
                result = model(frame)
                #get the height and the width of the frame
                height, width, _ = frame.shape

            #(001: nothing  / 011: reversed on x axis /100 : left /101: titled_right/111:tilted_left)
                if(result.pandas().xyxy[0].empty):
                    led_correct.off()
                    led_defective1.off()
                    led_defective2.off()
                    led_defective3.on()
                    print("Nothing")
                else:
                    for index,row in  result.pandas().xyxy[0].iterrows():
                        print(row[6])
                        # Define a bounding box
                        xmin, ymin, xmax, ymax = row[0], row[1],row[2],row[3]
                        # Calculate the center of the bounding box
                        center_x = (xmin + xmax) / 2
                        if(center_x < width/2):
                            led_correct.off()
                            led_defective1.on()
                            led_defective2.off()
                            led_defective3.off()

                        else:
                            if row[6] == "Normal":
                    #           print("Normal")
                                led_correct.on()
                                led_defective1.off()
                                led_defective2.off()
                                led_defective3.off()

                            if row[6] == "Inversed" :
                     #              print("Inversed")
                                led_correct.off()
                                led_defective1.off()
                                led_defective2.on()
                                led_defective3.on()
                            if row[6] == "Titled_right" :
                    #               print("Titled_right")
                                led_correct.off()
                                led_defective1.on()
                                led_defective2.off()
                                led_defective3.on()
                            if row[6] == "Titled_left":
                    #               print("Titled_right")
                                led_correct.off()
                                led_defective1.on()
                                led_defective2.on()
                                led_defective3.on()
                

                
                frame = np.squeeze(result.render())
                
             #   cv.imshow('FRAME',frame)
                if cv.waitKey(500)&0xFF==27:
                    break
                
                break
        


GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=toggle_led,bouncetime=500)

               
try:
    while True:
        
        state_automat = GPIO.input(AUTOMAT_PIN)
        print("autmat state  = "+ str(state_automat))
        
        if(state_automat==0):
                image_count = 1
                print("image add")
        continues_mode()
        optimal_mode(image_count,state_automat)
        if(state_automat ==1):
                image_count =0
        
 
        

except KeyboardInterrupt:
    GPIO.cleanup()
                


               

                
