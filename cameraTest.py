import cv2
import datetime  
import pandas as pd
import numpy as np


vid = cv2.VideoCapture(0)
i = 0
df = pd.DataFrame()
df1=[]
df2=[]

while True:
      
    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    frame = cv2.resize(frame,(256,128))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    if ret == False:
        break
    print(datetime.datetime.now())

    # Display the resulting frame
    cv2.imshow('frame', frame)
    cv2.imwrite('Imagesamples/'+str(i)+'.jpg', frame)
    time=datetime.datetime.now()
    df1.append(str(i)+'.jpg')
    df2.append(str(time))
   
    

   
    i += 1
      
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        
        break
df['image']=pd.Series(df1)
df['time']=pd.Series(df2)
df.to_csv('out_images.csv')  
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
