#include <iostream>
#include "mbed.h"
#include "bbcar.h"
#include "bbcar_rpc.h"
using namespace std;

/* BBcar */
Ticker servo_ticker;
PwmOut pin5(D5); // left wheel (yellow)
PwmOut pin6(D6); // right wheel (orange)
BBCar car(pin5, pin6, servo_ticker);

/* Xbee */
BufferedSerial xbee(D1, D0); //tx,rx

/* Uart */
BufferedSerial pc(USBTX,USBRX); //tx,rx
BufferedSerial uart(D10,D9); //tx,rx

/* DigitalOut */
DigitalOut led1(LED1); // for aptag
DigitalOut led2(LED2); // for line 
DigitalOut led3(LED3); // for park
DigitalOut is_start(D2); // for start signal (py)
DigitalOut is_end(D3);   // for end signal (py)
DigitalOut d4(D4);     // for ping's LED(red)
DigitalInOut d11(D11); // for ping
RpcDigitalOut RPCled1(LED1,"LED1"); 
RpcDigitalOut RPCled2(LED2,"LED2");
RpcDigitalOut RPCled3(LED3,"LED3");
RpcDigitalOut RPCd2(D2,"start");
RpcDigitalOut RPCd3(D3,"end"); 

/* Ping */


////////////////////////////////////////////////////

/* Thread */
Thread rpc_thread;
Thread park_thread;
Thread line_thread;
Thread aptag_thread;
Thread ping_thread;

/* EventQueue */
EventQueue rpc_event;
EventQueue park_event;
EventQueue line_event;
EventQueue aptag_event;
EventQueue ping_event;

/* Function */
void readRPC();   // read RPC command
void park();
void line();
void aptag();
void dectPing();

////////////////////////////////////////////////////

int main() 
{
   /* set up three mode */
   rpc_event.call(&readRPC);
   park_event.call(&park);
   line_event.call(&line);
   aptag_event.call(&aptag);
   //ping_event.call(&dectPing);
   rpc_thread.start(callback(&rpc_event, &EventQueue::dispatch_forever));
   park_thread.start(callback(&park_event, &EventQueue::dispatch_forever));
   line_thread.start(callback(&line_event, &EventQueue::dispatch_forever));
   aptag_thread.start(callback(&aptag_event, &EventQueue::dispatch_forever));
   //ping_thread.start(callback(&ping_event, &EventQueue::dispatch_forever));

   //readRPC();
   dectPing();
}
////////////////////////////////////////////////////

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

void dectPing()
{
   parallax_ping ping(d11);

   while (1) {
      if(float(ping) < 20) {
         d4 = 1;

         if(!led1) {
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