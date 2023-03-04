import urllib.request
import cv2 as cv
import numpy as np


while True:
    rectanglesList = []
    imgResponse = urllib.request.urlopen("http://192.168.43.107/capture?")
    print("s")
    imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
    frame = cv.imdecode(imgNp,-1)
    cv.imshow('Window',frame)
    print("The logo is composed by " + str(len(rectanglesList)) + " objects")
    key = cv.waitKey(500)
    if key == (ord('q')):
        break



cv.destroyAllWindows()
