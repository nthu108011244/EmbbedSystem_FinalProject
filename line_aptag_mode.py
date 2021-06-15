import pyb, sensor, image, time, math
enable_lens_corr = False # turn on for straighter lines...
sensor.reset()
sensor.set_pixformat(sensor.RGB565) # grayscale is faster
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()

# apriltag default size
f_x = (2.8 / 3.984) * 160 # find_apriltags defaults to this if not set
f_y = (2.8 / 2.952) * 120 # find_apriltags defaults to this if not set
c_x = 160 * 0.5 # find_apriltags defaults to this if not set (the image.w * 0.5)
c_y = 120 * 0.5 # find_apriltags defaults to this if not set (the image.h * 0.5)

uart = pyb.UART(3,9600,timeout_char=1000)
uart.init(9600,bits=8,parity = None, stop=1, timeout_char=1000)

while(True):
   clock.tick()
   img = sensor.snapshot()

   is_tag = 0
   is_line = 0

   # apriltag mode
   for tag in img.find_apriltags(fx=f_x, fy=f_y, cx=c_x, cy=c_y): # defaults to TAG36H11
      is_tag = 1
      img.draw_cross(tag.cx(), tag.cy(), color = (0, 255, 0))
      if (tag.cx() < 50):
         img.draw_rectangle(tag.rect(), color = (0, 100, 255))
         uart.write(("d").encode())
         print("%d d" % tag.cx())
      elif (tag.cx() > 110):
         img.draw_rectangle(tag.rect(), color = (0, 100, 255))
         uart.write(("a").encode())
         print("%d a" % tag.cx())
      else:
         img.draw_rectangle(tag.rect(), color = (255, 0, 0))
         uart.write(("w").encode())
         print("%d w" % tag.cx())

   if is_tag:
      time.sleep(0.5)
      continue # get apriltag -> skip line mode

   # line mode
   # img = sensor.snapshot()
   if enable_lens_corr: img.lens_corr(1.8) # for 2.8mm lens...
   for l in img.find_line_segments(merge_distance = 30, max_theta_diff = 45):
      if ((is_line == 0) & (40 <= l.x1()) & (l.x1() <= 120) & (40 <= l.x2()) & (l.x2() <= 120) \
      & ((l.y1() <= 5) | (l.y2() <= 5))):
         img.draw_line(l.line(), color = (0, 255, 0))
         is_line = 1
         data = (l.x1(), l.y1(), l.x2(), l.y2())
      else:
         img.draw_line(l.line(), color = (255, 0, 0))

   if is_line == 1:
      uart.write(("y %d %d %d %d\n" % data).encode())
      print("y %d %d %d %d\n" % data)
   else:
      uart.write(("n\n").encode())
      print("n\n")


