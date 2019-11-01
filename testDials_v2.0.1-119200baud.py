import serial
import sys, traceback

from time import sleep

INTERFACE = '/dev/cu.PL2303-0030134' #!!!change this to your personal device

dialsPosition=[-1,-1,-1,-1,-1,-1,-1,-1]
dialsCounter=[0,0,0,0,0,0,0,0]
dialDirection=[0,0,0,0,0,0,0,0]

print( "IBM Python dials 6094-010 V1.0.0" )

dials = serial.Serial(INTERFACE, 119200, timeout=1, parity=serial.PARITY_ODD, bytesize=8)

dials.flushInput()
dials.flush()

#check to see if dials are connected:
dials.write(chr(0x06))  #??Probably a bit-signified byte
status = dials.read(1)  #also:  potential race condition here:  will the output of the D&B be ready by the time this line is executed?

if status:
  if status == chr(0x08):
    print "Dials connected!"
    print ("status: ", status)
  else:
    print "Unexpected status byte:", ord(status)
else:
  print( "FAIL: dials not found, NULL" )
  print( "Exiting IBM Python dials program!" )
  dials.close()
  sys.exit(0)

# reset dials: 0x01
dials.write( chr(0x01) )

sleep(1.0) # Time in seconds.

# configure dials for output - Initialize Dials:
dials.write( chr(0x08) )

# set dial precision: 0xC8 [byte]
# set dial precision to 8 bits per dial
dials.write(chr(0xC8))
dials.write(chr(0xFF)) 
#the above code looks suspicous, need to understand whats going on:
# Do the D&B use sequential writes in some predetermined order or 
# is it using a bit-wise single byte for writing?

print "Dials are ready to send data!"
print "Turn dial to display value:"
#generate dial layout:

for index in xrange(0,8):
  print "Dial %d: %s direction %s counter" %(index+1, '   ', ' ')

_direction = 0
_position = 0

try:
  while True:
    pass
    value = dials.read(2)
    if value:
      H_byte = ord(value[0])  # implies H byte=first, and L byte is the second.
      L_byte = ord(value[1])
      HL_word = (H_byte << 8) + L_byte  #comment above confirmed
      dialNo = (H_byte >> 3) & 0x07
      position = ((H_byte << 7) & 0xFF) | (L_byte & 0x7F)
      direction= (H_byte >> 2) & 0x01

      # Increment or decrement counter:
      
      # if dialsPosition[dialNo] < position:
      #   dialsCounter[dialNo]=dialsCounter[dialNo]+1
            
      # if dialsPosition[dialNo] > position:
      #   dialsCounter[dialNo]=dialsCounter[dialNo]-1

      # Something with this logic goes nuts, and sometimes goes -64???
      # if (position >= dialsPosition[dialNo]) and dialDirection[dialNo] < 1:
      #   dialsCounter[dialNo]=dialsCounter[dialNo]+1

      # if (position <= dialsPosition[dialNo]) and dialDirection[dialNo] > 0:
      #   dialsCounter[dialNo]=dialsCounter[dialNo]-1


      test=direction*248-position

      if (test > 0):
        dialsCounter [dialNo] -= 1;
      elif (test < 1 and direction > 0):
        dialsCounter [dialNo] -= 1;
      else:
        dialsCounter [dialNo] += 1;
      


      # if direction < 1 and ((_position-position) < _position):
      #   dialsCounter [dialNo]=dialsCounter[dialNo]+1
      # elif direction > 0 and ((_position-position) < _position):
      #   dialsCounter [dialNo]=dialsCounter[dialNo]-1

      _position=position
      _direction=direction
      
      #assignment of new position to dialsPosition array
      dialsPosition[dialNo]=position

      print("\033[8A"),
      print chr(0xd),
      
      for index in xrange(0,8):
        if dialsPosition[index] > -1:
          print "Dial %d: %.3d direction %d counter %8d" %(index+1, dialsPosition[index], direction, dialsCounter[index])
        else:
          print "Dial %d: %s direction %s counter %8d" %(index+1, '   ', ' ', dialsCounter[index])
          pass
        pass
      # print chr(0x0d),
      sys.stdout.flush()

      # print "Dial ", dialNo+1, "Position: ", dialsPosition[dialNo], chr(0x0d),
      # sys.stdout.flush()
      
      # test statment to see value of dial in array:
      #print "Dial ", dialNo+1, "Position: ", dialsPosition[dialNo]

      #print "Dial ", dialNo+1," Position: ", position
      #print "HL_word: ", bin(HL_word) #BINARY output of H_byte + L_byte
except KeyboardInterrupt:
  print("\033[8B")
  print "Control-C received.  IBM dials terminating!"
  dials.close()
  pass
