#!/usr/bin/env python
import RPi.GPIO as GPIO #for importing gpio functionality
import socket
import pandas as pd
import curses
import datetime
#import cv2

df = pd.DataFrame()
df1 = []
df2 = []
df3 = []
import datetime 
data = (None,None)#need to read the values into data
screen = curses.initscr()
curses.noecho() 
curses.cbreak()
screen.keypad(True)
screen.nodelay(True)

def server_setup():
    HOST = "192.168.0.166"  
    PORT = 1234  

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((HOST, PORT))
    return server



def setup():
    frequency = 1000 

    Right_CW = 13 
    Right_CCW = 6
    Left_CCW = 19
    Left_CW = 26
    ENRight = 20
    ENLeft = 21

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Right_CW,GPIO.OUT)
    GPIO.setup(Right_CCW,GPIO.OUT)
    GPIO.setup(Left_CCW,GPIO.OUT)
    GPIO.setup(Left_CW,GPIO.OUT)
    GPIO.setup(ENRight,GPIO.OUT)
    GPIO.setup(ENLeft,GPIO.OUT)

    Right_PWM = GPIO.PWM(ENRight,frequency)
    Left_PWM = GPIO.PWM(ENLeft,frequency)

    Right_PWM.start(0)
    Left_PWM.start(0)

    GPIO.setwarnings(False)


    return Right_PWM, Left_PWM, Left_CW, Right_CW, Left_CCW, Right_CCW


def mapped(x,y):
    return (x - 512) * (100 - 0) // (1024 - 512) + 0, (y - 512) * (100 - 0) // (1024 - 512) + 0


def movement(right_speed,left_speed, Left_CMD, Right_CMD):
    if Left_CMD == Left_CW: 
        GPIO.output(Left_CCW,False)

    if  Right_CMD == Right_CW:
        GPIO.output(Right_CCW,False)

    if Left_CMD == Left_CCW: 
        GPIO.output(Left_CW,False)

    if  Right_CMD == Right_CCW:
        GPIO.output(Right_CW,False)

    Right_PWM.ChangeDutyCycle(abs(right_speed)//1.8)
    Left_PWM.ChangeDutyCycle(abs(left_speed)//1.8)
    GPIO.output(Left_CMD,True)
    GPIO.output(Right_CMD,True)



if __name__ == "__main__":
    Right_PWM, Left_PWM, Left_CW, Right_CW, Left_CCW, Right_CCW =  setup()
    server = server_setup()
    #vid = cv2.VideoCapture(0)
    try:
        while True:
            #ret, frame = vid.read()
            #frame = cv2.resize(frame,(128,128))
            #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY )
            data = server.recv(1024)

            if not data:
                break
                
            #if cv2.waitKey(1) & 0xFF == ord('q'):
               # break
              
            try:
                data = data.decode('utf-8')
                data = data[1:-3].split(',')
                data = tuple(map(int,data))
                if len(data) == 1:
                    data = (513,513)
            except Exception as e:
                data = (513,513)

            right_speed,left_speed = mapped(data[0],data[1])
            if data[0]==513 and data[1]==513:
                continue
            else:
                time=datetime.datetime.now()
                df3.append(time)
                df1.append(data[0])
                df2.append(data[1])
           

            if  left_speed > 5 and right_speed > 5:
                #print(f"Forward -> Left : {left_speed} right : {right_speed}")
                movement(right_speed,left_speed,Left_CW, Right_CW)

            elif left_speed > 5 and right_speed < 5:
                #print(f"Right -> Left : {left_speed} right : {right_speed}")
                movement(right_speed,left_speed,Left_CCW, Right_CW)

            elif left_speed < 5 and right_speed > 5:
                #print(f"Left -> Left : {left_speed} right : {right_speed}")
                movement(right_speed,left_speed,Left_CW, Right_CCW)

            elif left_speed < -10 and right_speed < -10 :
                #print(f"Backward -> Left : {left_speed} right : {right_speed}")
                movement(right_speed,left_speed,Left_CCW, Right_CCW)
            else:
                #print(f"Stop -> Left : {left_speed} right : {right_speed}")
                movement(0,0,Left_CCW, Right_CCW)
#             
            char = screen.getch() #used to get the keypress
                            
            if char == ord('q'):
                df['X']=pd.Series(df1)
                df['Y']=pd.Series(df2)
                df['Time']=pd.Series(df3)
                df.to_csv('Out_Joystick.csv')   #if q is pressed then quit the program
                GPIO.cleanup()
                curses.nocbreak(); screen.keypad(0); curses.echo()
                curses.endwin()
           
                break
             

        

            #cv2.imshow('frame', frame)


    except Exception as e:
        print(e)
        GPIO.cleanup()

    
                

