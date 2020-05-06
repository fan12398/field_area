import serial

ser = serial.Serial('/dev/ttyAMA0',115200)

for i in range(100):
    txt = 'hello'+str(i)+'\r\n'
    ser.write(txt.encode())

txt = 'hello end\r\n'
ser.write(txt.encode())

while(1):
    dat = ser.readline()
    print(dat)
