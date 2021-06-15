import time
import serial
import sys,tty,termios

serdev = '/dev/ttyUSB0'
s = serial.Serial(serdev, 9600)

while True:
    if s.readable():
        message = s.readline()
        print(message.decode())