#!/bin/bash
echo $(date) 
cd ~/home/pi/Downloads/tflite_classification_demo/hello
source bin/activate
cd ../../../
cd ~/Documents/ineuron/
python3 self-driving.py
