import cv2
import torch
import numpy as np
import pandas as pd
import urllib.request

model = torch.hub.load('.', 'custom', path='bestV1.pt', source='local') 

model.conf = 0.85
    

while True:
    imgResponse = urllib.request.urlopen("http://192.168.154.38/capture?")
    imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
    frame = cv.imdecode(imgNp,-1)
    result = model(frame)
    for index,row in  result.pandas().xyxy[0].iterrows():
        if row[6]!= "Normal" and row[6]!= "Inversed":
            print("Nothing")
        else:
            print(row[6])
    frame = np.squeeze(result.render())
    cv2.imshow('FRAME',frame)
    if cv2.waitKey(500)&0xFF==27:
        break
cap.release()
cv2.destroyAllWindows()