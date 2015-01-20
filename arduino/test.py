import serial
import time
port = serial.Serial(port='/dev/ttyACM0',baudrate=9600,timeout=1)

time.sleep(10)
port.setDTR(level=0)
time.sleep(1)
#command = str.encode('ON') + '\r'
port.write('ON\r') # if writing directly in the function, no str.encode needed
port.close()
