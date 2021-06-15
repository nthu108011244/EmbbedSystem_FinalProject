import time
import serial
import sys,tty,termios
class _Getch:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def get():
    inkey = _Getch()
    while(1):
        k=inkey()
        if k!='':break
    if k=='\x1b':
        k2 = inkey()
        k3 = inkey()
        if k3=='A':
            print ("go forward")
            s.write("/goStraight/run 100 \n".encode())
        if k3=='B':
            print ("go back")
            s.write("/goStraight/run -100 \n".encode())
        if k3=='C':
            print ("turn clockwise")
            s.write("/turn/run 100 -0.3 \n".encode())
        if k3=='D':
            print ("turn counterclockwise")
            s.write("/turn/run 100 0.3 \n".encode())
        time.sleep(1)
        s.write("/stop/run \n".encode())
    elif k=='q':
        print ("quit")
        return 0
    else:
        print ("not an arrow key!")
    return 1

def get_command():
    command = input("[Home]>>> ")
    if command == "over": 
        return 0
    elif command == "test":
        test_mode()
        return 1
    elif command == "park":
        park_mode()
        return 1
    elif command == "line":
        line_mode()
        return 1
    elif command == "aptag":
        aptag_mode()
        return 1
    else:
        print(command[:] + " is not keyword")
        return 1

def test_mode():
    print("[Test]: enter test mode")

    command = input("[Test]>>> ")
    while command != "quit":

        if command == "ww":
            go_forward(10)
            command = input("[Test]>>> ")
            continue
        elif command == "ss":
            go_back(10)
            command = input("[Test]>>> ")
            continue
        elif command == "dd":
            spin_clockwise()
            command = input("[Test]>>> ")
            continue
        elif command == "aa":
            spin_couneterclockwise()
            command = input("[Test]>>> ")
            continue

        str = command.split()
        if len(str) < 2:
            print (f"{command} is not a keyword")
            dirct = "none"
        else :
            dirct = str[0]
            t = float(str[1])
        

        if dirct == "w":
            print(f"go forward {t} cm")
            s.write("/goStraight/run 200 \n".encode())
            time.sleep(t / fv)
            s.write("/stop/run \n".encode())
        elif dirct == "s":
            print(f"go back {t} cm")
            s.write("/goStraight/run -200 \n".encode())
            time.sleep(t / bv)
            s.write("/stop/run \n".encode())
        elif dirct == "d":
            print (f"spin clockwise {t} sec")
            s.write("/turn/run 200 1 \n".encode())
            time.sleep(t)
            s.write("/stop/run \n".encode())
        elif dirct == "a":
            print (f"spin counterclockwise {t} sec")
            s.write("/turn/run 200 -1 \n".encode())
            time.sleep(t)
            s.write("/stop/run \n".encode())
        command = input("[Test]>>> ")

    print("[Test]: leave test mode")

def park_mode():
    print("[Park]: enter park mode")

    s.write("/LED3/write 1 \n".encode())
    command = input("[Park]>>> ")
    while command != "quit":
        str = command.split(' ')
        if len(str) < 2:
            print (f"{command} is not a keyword")
            dirct = "none"
        else :
            d1 = float(str[0])
            d2 = float(str[1])
            dirct = str[2]

        if dirct == "west":
            s.write("/start/write 1 \n".encode())
            go_back(d1 + 15) # 5 is the half width of BBcar, 12 is the width of space
            time.sleep(1)
            spin_couneterclockwise() 
            time.sleep(1)
            go_back(d2 + 10) # 15 is the half length of BBcar
            s.write("/end/write 1 \n".encode())
        elif dirct == "east":
            s.write("/start/write 1 \n".encode())
            go_back(d1 + 15) # 5 is the half width of BBcar, 12 is the width of space
            time.sleep(1)
            spin_clockwise() 
            time.sleep(1)
            go_back(d2 + 10) # 15 is the half length of BBcar
            s.write("/end/write 1 \n".encode())
        command = input("[Park]>>> ")
        s.write("/LED3/write 1 \n".encode())

    s.write("/LED3/write 0 \n".encode())
    print("[Park]: leave park mode")

def line_mode():
    print("[Line]: enter line mode")

    s.write("/LED2/write 1 \n".encode())
    s.write("/start/write 1 \n".encode())
    command = input("[Line]>>> ")
    while command != "quit":
        s.write("/LED2/write 1 \n".encode())
        s.write("/start/write 1 \n".encode())
        command = input("[Line]>>> ")
    s.write("/LED2/write 0 \n".encode())
    stop()

    print("[Line]: leave line mode")

def aptag_mode():
    print("[Aptag]: enter aptag mode")
    
    s.write("/LED1/write 1 \n".encode())
    s.write("/start/write 1 \n".encode())
    command = input("[Aptag]>>> ")
    while command != "quit":
        s.write("/LED1/write 1 \n".encode())
        s.write("/start/write 1 \n".encode())
        command = input("[Aptag]>>> ")
    s.write("/LED1/write 0 \n".encode())
    stop()

    print("[Aptag]: leave aptag mode")


def go_forward(length):
    print(f"go forward {length} cm")
    s.write("/goStraight/run 200 \n".encode())
    time.sleep(length / fv)
    s.write("/stop/run \n".encode())

def go_back(length):
    print (f"go back {length} cm")
    s.write("/goStraight/run -200 \n".encode())
    time.sleep(length / bv)
    s.write("/stop/run \n".encode())

def spin_clockwise():
    print ("spin clockwise 90 degree")
    s.write("/turn/run 200 1 \n".encode())
    time.sleep(0.4)
    s.write("/stop/run \n".encode())

def spin_couneterclockwise():
    print ("spin counterclockwise 90 degree")
    s.write("/turn/run 200 -1 \n".encode())
    time.sleep(0.45)
    s.write("/stop/run \n".encode())

def stop():
    s.write("/stop/run \n".encode())


# main()
if len(sys.argv) < 1:
    print ("No port input")
s = serial.Serial(sys.argv[1])
fv = 22    # forward velocity (cm/s)
bv = 21.8  # backward velocity (cm/s)
while get_command():
    i = 0
