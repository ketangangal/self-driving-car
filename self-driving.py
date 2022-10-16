#!/usr/bin/env python
import RPi.GPIO as GPIO  # for importing gpio functionality
import socket
import pandas as pd
import numpy as np
import curses
import datetime
from tflite_runtime.interpreter import Interpreter
import cv2

import datetime

data = (None, None)  # need to read the values into data


def predict(img, tflite_interpreter, input_details, output_details):
    # print(img.shape)
    img = img.reshape(128, 256, 3)
    img = np.float32(img)
    input_tensor = np.array(np.expand_dims(img, 0), dtype=np.float32)
    # print(input_tensor.shape)
    tflite_interpreter.set_tensor(input_details[0]['index'], input_tensor)
    tflite_interpreter.invoke()
    output_details = tflite_interpreter.get_output_details()

    pred = tflite_interpreter.get_tensor(output_details[0]['index'])
    result = np.squeeze(pred)
    x, y = int(np.ceil(result[0])), int(np.ceil(result[1]))
    return x, y


def setup():
    frequency = 1000

    Right_CW = 13
    Right_CCW = 6
    Left_CCW = 19
    Left_CW = 26
    ENRight = 20
    ENLeft = 21

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Right_CW, GPIO.OUT)
    GPIO.setup(Right_CCW, GPIO.OUT)
    GPIO.setup(Left_CCW, GPIO.OUT)
    GPIO.setup(Left_CW, GPIO.OUT)
    GPIO.setup(ENRight, GPIO.OUT)
    GPIO.setup(ENLeft, GPIO.OUT)

    Right_PWM = GPIO.PWM(ENRight, frequency)
    Left_PWM = GPIO.PWM(ENLeft, frequency)

    Right_PWM.start(0)
    Left_PWM.start(0)

    GPIO.setwarnings(False)

    return Right_PWM, Left_PWM, Left_CW, Right_CW, Left_CCW, Right_CCW


def mapped(x, y):
    return (x - 512) * (100 - 0) // (1024 - 512) + 0, (y - 512) * (100 - 0) // (1024 - 512) + 0


def movement(right_speed, left_speed, Left_CMD, Right_CMD):
    if Left_CMD == Left_CW:
        GPIO.output(Left_CCW, False)

    if Right_CMD == Right_CW:
        GPIO.output(Right_CCW, False)

    if Left_CMD == Left_CCW:
        GPIO.output(Left_CW, False)

    if Right_CMD == Right_CCW:
        GPIO.output(Right_CW, False)

    Right_PWM.ChangeDutyCycle(abs(right_speed) // 1.8)
    Left_PWM.ChangeDutyCycle(abs(left_speed) // 1.8)
    GPIO.output(Left_CMD, True)
    GPIO.output(Right_CMD, True)


if __name__ == "__main__":
    Right_PWM, Left_PWM, Left_CW, Right_CW, Left_CCW, Right_CCW = setup()
    vid = cv2.VideoCapture(0)

    tflite_interpreter = Interpreter(model_path='model-v5.tflite')
    tflite_interpreter.allocate_tensors()

    input_details = tflite_interpreter.get_input_details()
    output_details = tflite_interpreter.get_output_details()

    print("== Input details ==")
    print("name:", input_details[0]['name'])
    print("shape:", input_details[0]['shape'])
    print("type:", input_details[0]['dtype'])

    print("\n== Output details ==")
    print("name:", output_details[0]['name'])
    print("shape:", output_details[0]['shape'])
    print("type:", output_details[0]['dtype'])

    try:
        while True:
            ret, frame = vid.read()
            frame = cv2.resize(frame, (256, 128))
            x, y = predict(frame, tflite_interpreter, input_details, output_details)
            print(f"Speed X -> {x}, Speed Y-> {y}")
            data = (x, y)

            right_speed, left_speed = mapped(data[0], data[1])

            if left_speed > 5 and right_speed > 5:
                # print(f"Forward -> Left : {left_speed} right : {right_speed}")
                movement(right_speed, left_speed, Left_CW, Right_CW)

            elif left_speed > 5 and right_speed < 5:
                # print(f"Right -> Left : {left_speed} right : {right_speed}")
                movement(right_speed, left_speed, Left_CCW, Right_CW)

            elif left_speed < 5 and right_speed > 5:
                # print(f"Left -> Left : {left_speed} right : {right_speed}")
                movement(right_speed, left_speed, Left_CW, Right_CCW)

            elif left_speed < -10 and right_speed < -10:
                # print(f"Backward -> Left : {left_speed} right : {right_speed}")
                movement(right_speed, left_speed, Left_CCW, Right_CCW)
            else:
                # print(f"Stop -> Left : {left_speed} right : {right_speed}")
                movement(0, 0, Left_CCW, Right_CCW)

    except Exception as e:
        print(e)
        GPIO.cleanup()
