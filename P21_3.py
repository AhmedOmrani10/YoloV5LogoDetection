from setUp import *

       
setUp = setUp()
try:
    
    while True:
        
        if setUp.image_count == 1 and setUp.state_automat == 1:
            setUp.image_count, setUp.state_automat = setUp.optimal_mode()

except KeyboardInterrupt:
    GPIO.cleanup()
