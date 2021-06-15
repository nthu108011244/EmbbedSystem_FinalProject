# EmbbedSystem_FinalProject

# mbed (mian.cpp)
Each part has its own thread and eventQueue, moreover, ping use the main thread.

## BBCar
Control the BBCar.
``` bash
''' global variable '''
Ticker servo_ticker;
PwmOut pin5(D5); # left wheel 
PwmOut pin6(D6); # right wheel (orange)
BBCar car(pin5, pin6, servo_ticker);
```

## openMV
Receive signal from openMV.
``` bash
''' global variable '''
BufferedSerial uart(D10,D9); # tx,rx
```

## Ping
If the distance is smaller than 20 (cm), then red LED and LED3 wiil turn on, what's more, BBCar wiil go back.
``` bash
''' global variable '''
DigitalOut d4(D4);      # for red LED
DigitalInOut d11(D11);  # for ping

''' function '''
void dectPing()
{
   parallax_ping ping(d11);

   while (1) {
      if (float(ping) < 20) {
         d4 = 1;

         if (!led1) {
            car.stop();
            car.goStraight(-200);
            ThisThread::sleep_for(100ms);
            car.stop();
         }
         else if (float(ping) < 10) {
            char buffer[] = "[Aptag]: mission complete\n"; 
            xbee.write(buffer, 26);
         }
      }
      else {
         d4 = 0;
      }

      //char buffer[20];
      //sprintf(buffer, "ping: %.2f\r\n", float(ping));
      //pc.write(buffer, sizeof(buffer));
      ThisThread::sleep_for(100ms);
   }
}
```

## RPC
Always read RPC command from PC (python).
``` bash
''' global variable '''
BufferedSerial xbee(D1, D0); #  tx, rx
RpcDigitalOut RPCled1(LED1,"LED1"); 
RpcDigitalOut RPCled2(LED2,"LED2");

Thread rpc_thread;
EventQueue rpc_event;

''' function '''
void readRPC()
{
   char buf[256], outbuf[256];
   FILE *devin = fdopen(&xbee, "r");
   FILE *devout = fdopen(&xbee, "w");
   while (1) {
      memset(buf, 0, 256);
      for( int i = 0; ; i++ ) {
         char recv = fgetc(devin);
         if(recv == '\n') {
            printf("\r\n");
            break;
         }
         buf[i] = fputc(recv, devout);
      }
   RPC::call(buf, outbuf);
   }
}
```

## Parking mode
Here, mbed does nothing in parking mode.
``` bash
''' global variable '''
DigitalOut led3(LED3); # enable
DigitalOut is_start(D2); # for start signal (py)
DigitalOut is_end(D3);   # for end signal (py)

Thread park_thread;
EventQueue park_event;

''' function '''
void park()
{
   while (1) {
      if (led3) {
         if (is_start) {
            is_start = 0;
            char buffer[] = "[Park]: mission start\n"; 
            xbee.write(buffer, 22);
         }
         if (is_end) {
            is_end = 0;
            char buffer[] = "[Park]: mission complete\n"; 
            xbee.write(buffer, 25);
         }
      }
   }
}
```

## Line-following mode
Read the signal from openMV, and do the corresponding action.\
y -> go.\
n -> stop.
``` bash
''' global variable '''
DigitalOut led2(LED2); # enable 
DigitalOut is_start(D2); # for start signal (py)
DigitalOut is_end(D3);   # for end signal (py)

Thread line_thread;
EventQueue line_event;

''' function '''
void line()
{
   bool is_endline;
   bool is_sendend;
   uart.set_baud(9600);
   while (1) {
      if (led2) {
         if (is_start) {
            is_start = 0;
            is_endline = 0;
            is_sendend = 0;
            char buffer[] = "[Line]: mission start\n"; 
            xbee.write(buffer, 22);
         }

         if (uart.readable()) {
            char recv[1];
            uart.read(recv, sizeof(recv));

            if (recv[0] == 'y') car.goStraight(200);
            else if (recv[0] == 'n') {
               is_endline = 1;
               car.stop();
            }

            if (!led2) car.stop();
         }

         if (is_endline && !is_sendend) {
            is_sendend = 1;
            char buffer[] = "[Line]: mission complete\n"; 
            xbee.write(buffer, 25);
         }
      }
   }
}
``` 

## AprilTag-following mode
Read the signal from openMV, and do the corresponding action.\
w -> go.\
d -> spin clockwise.\
a -> soin counterclockwise.
``` bash
''' global variable '''
DigitalOut led1(LED1); # enable
DigitalOut is_start(D2); # for start signal (py)
DigitalOut is_end(D3);   # for end signal (py)

Thread aptag_thread;
EventQueue aptag_event;

''' function '''
void aptag()
{
   uart.set_baud(9600);
    while (1) {
      if (uart.readable()) {
         char recv[1];
         uart.read(recv, sizeof(recv));
         //pc.write(recv, sizeof(recv));
         if (is_start && led1) {
            is_start = 0;
            char buffer[] = "[Aptag]: mission start\n"; 
            xbee.write(buffer, 23);
         }

         if (led1) {
            if (recv[0] == 'w') {
               car.goStraight(200);
               ThisThread::sleep_for(100ms);
            }
            else if (recv[0] == 'd') {
               car.turn(200, 1);
               ThisThread::sleep_for(100ms);
            }
            else if (recv[0] == 'a') {
               car.turn(200, -1);
               ThisThread::sleep_for(100ms);
            }
            car.stop();
            //ThisThread::sleep_for(100ms);
         }
      }  
   }
}
``` 
# PC (car_control.py)

## [Home]
Enter the keyword to get in the correspondong mode.
Enter "over" to shit down this project.
``` bash
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

```

## [Test]
This mode allow user to control BBCar arbitrarily.\
ww -> go forward 10 cm.\
ss -> go back 10 cm.\
dd -> spin clockwise 90 degrees.\
aa -> spin counterclockwise 90 degrees.\
w x -> go forward x cm.\
s x -> go back x cm.\
d t -> spin clockwise t sec.\
a t -> spin counterclockwise t sec.
``` bash
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
```

## [Park]
Park BBcar by enter "d1 d2 direction".
``` bash
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
```

## [Line]
Turn on the line-following mode in mbed.
``` bash
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

```

## [Aptag]
Turn on the AprilTag-following mode in mbed.
``` bash
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
```

# PC (car_message.py)
This code shows the message receiving from BBCar.
``` bash
import time
import serial
import sys,tty,termios

serdev = '/dev/ttyUSB0'
s = serial.Serial(serdev, 9600)

while True:
    if s.readable():
        message = s.readline()
        print(message.decode())
```
