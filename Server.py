import socket
import serial
import time

HOST = "192.168.0.166"
PORT = 1234

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
client, addr = server.accept()

print(f"Server Started at {HOST}:{PORT}")
print(f"Connected with client {client}")


def write_read():
    data = arduino.readline()
    return data


while True:
    value = write_read()
    try:
    	message = str(value.decode()).encode('utf-8')
    	print(message)
    	client.send(message)
    except:
    	client.send(str((513,513)).encode('utf-8'))
    
    
    
    
    
    
