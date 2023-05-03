
# Import required libraries
import cv2 as cv # OpenCV library for computer vision
import torch # PyTorch library for deep learning
import numpy as np # NumPy library for numerical computations
#import pandas as pd
import urllib.request  # urllib library for working with URLs
from gpiozero import LED # gpiozero library for working with GPIO pins
import RPi.GPIO as GPIO # Raspberry Pi library for working with GPIO pins
import time # time library for timing functions
import subprocess  # subprocess library for running shell commands

# Set a default prediction number
prediction_number = 0
# Set a default state of the two modes
state = False
# Set a default image number
image_count = 0
# Set a default trigger state
state_automat = 0

# Define some constants for pin numbers
#FAN_PIN = 18
AUTOMAT_PIN = 33
BUTTON_PIN = 22
READY_PIN = 17
RESULT_READY_PIN = 35
CORRECT_PIN = 18
DEFECTIVE1_PIN = 27
DEFECTIVE2_PIN = 22
DEFECTIVE3_PIN = 24

# Set up the GPIO pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RESULT_READY_PIN,GPIO.OUT)
GPIO.setup(AUTOMAT_PIN, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_PIN, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(FAN_PIN, GPIO.OUT)

# Set up the leds' pins
led_ready =LED(READY_PIN)
led_correct= LED(CORRECT_PIN)
led_defective1 = LED(DEFECTIVE1_PIN)
led_defective2 = LED(DEFECTIVE2_PIN)
led_defective3 = LED(DEFECTIVE3_PIN)

# Turn off the LEDs
led_ready.off()
led_correct.off()
led_defective1.off()
led_defective2.off()
led_defective3.off()

# Load the custom-trained computer vision model
model = torch.hub.load('.', 'custom', path='bestV2.pt', source='local') 

# Define the confidence for the model
model.conf = 0.85




# Define a function to change the state that controls the two modes (continues & oprtimal) based on a button press
def change_state(BUTTON_PIN):
	global state

	state = not(state)

def change_image_count(AUTOMAT_PIN):
        global image_count
        global state_automat
        image_count = 1
        state_automat = 1
        #print("state autmat inside inturrption: {}".format(state_automat))
        
# Define a function to control the temperature of the Raspberry Pi
def control_tempreture():
	
	temperature_c = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
	temperature_c = float(temperature_c.replace("temp=", "").replace("'C\n", ""))
	
	print("Temperature: {:.2f}°C ".format(temperature_c))
	#while temperature_c >= 85:
	#	GPIO.output(FAN_PIN, GPIO.HIGH)
	#	if temperature_c <= 40:
	#		GPIO.output(FAN_PIN, GPIO.LOW)
	#		break
			

		



# Define a function to check if the camera is connected
def check_connection():
        connected = False
        global imgResponse
        while not connected:
                    try:
                        imgResponse = urllib.request.urlopen("http://192.168.43.117/capture?",timeout = 5)
                        control_led('1')
                        connected = True
                    except:
                        control_led("111")
                        
# Define a function to predict the state of the logo
def predict():
        imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
        frame = cv.imdecode(imgNp,-1)
        return frame,model(frame)

# Define a function to control the leds based on state_code
def control_led(state_code):
    #(000 : normal /001: nothing  / 011: reversed on x axis /100 : left /101: titled_right/110:tilted_left)
    if state_code == "000":
        print("Normal")
        led_correct.on()
        led_defective1.off()
        led_defective2.off()
        led_defective3.off()
    elif state_code == "001":
        print("Nothing")
        led_correct.off()
        led_defective1.off()
        led_defective2.off()
        led_defective3.on()
    elif state_code == "011":
        print("Inverted")
        led_correct.off()
        led_defective1.off()
        led_defective2.on()
        led_defective3.on()
    elif state_code == "100":
        print("Left")
        led_correct.off()
        led_defective1.on()
        led_defective2.off()
        led_defective3.off()
    elif state_code == "101":
        print("Font wrong")
        led_correct.off()
        led_defective1.on()
        led_defective2.off()
        led_defective3.on()
    elif state_code == "110":
        print("logo is under")
        led_correct.off()
        led_defective1.on()
        led_defective2.on()
        led_defective3.on()
    elif state_code == "111":
        print("failed...")
        led_ready.off()
        led_correct.off()
        led_defective1.on()
        led_defective2.on()
        led_defective3.on()
    elif state_code =="1":
        led_ready.on()
        print("done")
            
                        
            
    else:
        print("Invalid state code")
                        
                        
                        
# Define a function to show the results of the prediction        
def show_result(result,width):
        bbox_height_part = None
        bbox_height_normal = None
        if(result.pandas().xyxy[0].empty):
                control_led("001")
                    
        else:  
                   #(000 : normal /001: nothing  / 011: inversed /100 : left /101: titled_right/110:tilted_left)
                    for index,row in  result.pandas().xyxy[0].iterrows():
                        # Define a bounding box
                        xmin, ymin, xmax, ymax = row[0], row[1],row[2],row[3]
                        # Calculate the center of the bounding box
                        center_x = (xmin + xmax) / 2
                        if(center_x < width/2):
                                control_led("100")
                        if row[6] == "part":
                            x1, y1, x2, y2 = row[:4].astype(int)
                            bbox_height_part = y2 - y1
                        elif row[6] == "Normal":
                            x1, y1n, x2, y2n = row[:4].astype(int)
                            bbox_height_normal = y2n - y1n
                        if bbox_height_part and bbox_height_normal:
                            ratio_position =  bbox_height_part /bbox_height_normal
                            # it has to be between 31 and 38
                            ratio_word = (y1-y1n)*100//(y2n-y1n)
                            bbox_height_part = None
                            bbox_height_normal = None
                            if(ratio_word>40):
                                control_led("101")
                            if(ratio_word>0.51):
                                control_led("110")
                        else:
                            if row[6] == "Normal":
                                    control_led("000")
                            if row[6] == "Inverted" :
                                    control_led("011")
                                   
                    


# Define a function for continuse mode 
def continues_mode():
         check_connection()
         frame,result = predict()
         #get the height and the width of the frame
         height, width, _ = frame.shape

         #(001: nothing  / 011: reversed on x axis /100 : left /101: titled_right/111:tilted_left)
         show_result(result,width)
         

         frame = np.squeeze(result.render())
         #   cv.imshow('FRAME',frame)
         #if cv.waitKey(500)&0xFF==ord('q'):
                # break
        
               
       
# Define a function for optimal mode 
def optimal_mode(image_count,state_automat):
        check_connection()
        frame, result = predict()
         #get the height and the width of the frame
        height, width, _ = frame.shape
        show_result(result,width)
        GPIO.output(RESULT_READY_PIN,1)
        # Read the state of the pin
        state_ready = GPIO.input(RESULT_READY_PIN)

        # Print the state of the pin
        print("State of GPIO pin 35: {}".format(state_ready))

        time.sleep(1)
        GPIO.output(RESULT_READY_PIN,0)
        state_ready = GPIO.input(RESULT_READY_PIN)
        print("State of GPIO pin 35: {}".format(state_ready))
       

       
       
        frame = np.squeeze(result.render())
        
        
        return 0 , 0
                
        #   cv.imshow('FRAME',frame)
        #if cv.waitKey(500)&0xFF==ord('q'):
                # break
        
                
        
       
                
        
# Set up an interrupt for the button
GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=change_state,bouncetime=500)
GPIO.add_event_detect(AUTOMAT_PIN, GPIO.RISING, callback=change_image_count,bouncetime=500)



               
try:
    while True:
	
        #control_tempreture() 
        #time.sleep(2) 
        #state_pin = GPIO.input(BUTTON_PIN)
        if(prediction_number ==0):
                time_s = time.time()
      
        if(state == 0):
                continues_mode()
                prediction_number+=1
                print(prediction_number)
                if(prediction_number == 10):
                        time_f = time.time()
                        print(str(time_f-time_s))
        
           
        #print("state autmat outside inturrption:{}".format(state_automat))
           
        if state and image_count ==1 and state_automat ==1:
                image_count,  state_automat = optimal_mode(image_count,state_automat)
      
        
      
               
        
 
        

except KeyboardInterrupt:
    GPIO.cleanup()
                


               

                

