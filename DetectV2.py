import cv2
import torch
import numpy as np
import pandas as pd

model = torch.hub.load('.', 'custom', path='bestV2.pt', source='local') 

model.conf = 0.85
cap=cv2.VideoCapture(0)

cv2.namedWindow('FRAME')

while True:
    ret,frame=cap.read()
    frame=cv2.resize(frame,(1020,500))
    result = model(frame)
    for index,row in  result.pandas().xyxy[0].iterrows():
        if row[6]!= "Normal" and row[6]!= "Inversed":
            print("Nothing")
        else:
            print(row[6])
    frame = np.squeeze(result.render())
    cv2.imshow('FRAME',frame)
    if cv2.waitKey(1)&0xFF==27:
        break
cap.release()
cv2.destroyAllWindows()