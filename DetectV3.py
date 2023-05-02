import cv2
import torch
import numpy as np
import pandas as pd

model = torch.hub.load('.', 'custom', path='bestV13.pt', source='local') 

model.conf = 0.8



cv2.namedWindow('FRAME')
tolerance =0

cap = cv2.VideoCapture(0)
ratios=[]
while True:
    ret, frame = cap.read()
    result = model(frame)

    bbox_height_part = None
    bbox_height_normal = None


    for index, row in result.pandas().xyxy[0].iterrows():
        if row[6] == "part":
            x1, y1, x2, y2 = row[:4].astype(int)
            logo_region = frame[y1:y2, x1:x2]
            bbox_height_part = y2 - y1
        elif row[6] == "Normal":
            x1, y1n, x2, y2n = row[:4].astype(int)
            bbox_height_normal = y2n - y1n
        else:
            
            bbox_height_part = None
            bbox_height_normal = None

        if bbox_height_part and bbox_height_normal:
            #ratio =  bbox_height_part /bbox_height_normal
            #print("Ratio of heights:", ratio)
            #print(" bbox_height_part"+str( bbox_height_part))
            #print("height"+str(bbox_height_normal//2))
            # it has to be between 31 and 38
            ratio = (y1-y1n)*100//(y2n-y1n)
            ratios.append(ratio)
            print(ratio)
            bbox_height_part = None
            bbox_height_normal = None


            


            #if per <= 50:
             #   print("logo above")
            #else:
             #   print("logo under")
        
           
            
                
            
       #  // 2:
          #  
        #else:
         #   

            

    frame = np.squeeze(result.render())
    cv2.imshow('FRAME', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
print("max"+str(max(ratios)))
print("min"+str(min(ratios)))