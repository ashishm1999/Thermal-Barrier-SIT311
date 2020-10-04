import RPi.GPIO as GPIO
import time
import time
import busio
import board
import adafruit_amg88xx
import statistics
import urllib.request as urllib2

# GPIO to LCD mapping
LCD_RS = 26 # Pi pin 37
LCD_E = 19 # Pi pin 35
LCD_D4 = 13 # Pi pin 33
LCD_D5 = 6 # Pi pin 31
LCD_D6 = 5 # Pi pin 29
LCD_D7 = 11 # Pi pin 23
Barrier = 21
Trig = 12
Echo = 25

# Device constants
LCD_CHR = True # Character mode
LCD_CMD = False # Command mode
LCD_CHARS = 16 # Characters per line (16 max)
LCD_LINE_1 = 0x80 # LCD memory location for 1st line
LCD_LINE_2 = 0xC0 # LCD memory location 2nd line

def thingspeak_post():#to post data on cloud and get a graph for the data
    Val1 = temp
    Val2 = allowed_count
    Val3 = Not_allowed_count
    URL='https://api.thingspeak.com/update?api_key='
    KEY='DNHF2A2U0KDVUJBF'
    HEADER='&field1={}&field2={}&field3={}'.format(Val1,Val2,Val3)
    NEW_URL=URL+KEY+HEADER
    print(NEW_URL)
    data=urllib2.urlopen(NEW_URL)

def checkdist():
    # set Trigger to HIGH
    GPIO.output(Trig, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(Trig, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(Echo) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(Echo) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance


# Define main program code
def main():
 
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM) # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT) # Set GPIO's to output mode
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_D4, GPIO.OUT)
    GPIO.setup(LCD_D5, GPIO.OUT)
    GPIO.setup(LCD_D6, GPIO.OUT)
    GPIO.setup(LCD_D7, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)
    GPIO.setup(Trig, GPIO.OUT)
    GPIO.setup(Echo, GPIO.IN)
    
    

# Initialize display
    lcd_init()

# Loop - send text and sleep 3 seconds between texts
# Change text to anything you wish, but must be 16 characters or less
    i2c = busio.I2C(board.SCL, board.SDA)
    amg = adafruit_amg88xx.AMG88XX(i2c)
    
    pwm=GPIO.PWM(21,100)                        ## PWM Frequency
    pwm.start(5)
    
    angle1=10
    duty1= float(angle1)/10 + 2.5               ## Angle To Duty cycle  Conversion
     
    angle2=160
    duty2= float(angle2)/10 + 2.5
    allowed_count = 0
    Not_allowed_count = 0;
    while True:
        dist = checkdist()
        print ("Measured Distance = %.1f cm" % dist)
        #time.sleep(1)
        if dist < 80:
            for row in amg.pixels:
                
                temp = statistics.mean(row)
                print(['{0:.1f}'.format(temp)])
                lcd_text(("Temperature:" + '{0:.1f}'.format(temp) ), LCD_LINE_1)
                time.sleep(2)
                
                if temp < 28:
                    pwm.ChangeDutyCycle(duty1)
                    time.sleep(0.8)
                    pwm.ChangeDutyCycle(duty2)
                    allowed_count = allowed_count + 1
                    print("People Allowed To enter: " + '{0:f}'.format(allowed_count) )
                    time.sleep(0.8)
                else:
                    Not_allowed_count = Not_allowed_count + 1
                    print("People Not Allowed To enter: " + '{0:f}'.format(Not_allowed_count))
                    GPIO.output(21,False)
                Val1 = temp
                Val2 = allowed_count
                Val3 = Not_allowed_count
                URL='https://api.thingspeak.com/update?api_key='
                KEY='DNHF2A2U0KDVUJBF'
                HEADER='&field1={}&field2={}&field3={}'.format(Val1,Val2,Val3)
                NEW_URL=URL+KEY+HEADER
                print(NEW_URL)
                data=urllib2.urlopen(NEW_URL)

            time.sleep(1)
        
    # End of main program code


    # Initialize and clear display
def lcd_init():
    lcd_write(0x33,LCD_CMD) # Initialize
    lcd_write(0x32,LCD_CMD) # Set to 4-bit mode
    lcd_write(0x06,LCD_CMD) # Cursor move direction
    lcd_write(0x0C,LCD_CMD) # Turn cursor off
    lcd_write(0x28,LCD_CMD) # 2 line display
    lcd_write(0x01,LCD_CMD) # Clear display
    time.sleep(0.0005) # Delay to allow commands to process

def lcd_write(bits, mode):
# High bits
    GPIO.output(LCD_RS, mode) # RS
    # GPIO.output(LCD_D0, False)
    # GPIO.output(LCD_D1, False)
    # GPIO.output(LCD_D2, False)
    # GPIO.output(LCD_D3, False)
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x10==0x10:
        GPIO.output(LCD_D4, True)
    if bits&0x20==0x20:
        GPIO.output(LCD_D5, True)
    if bits&0x40==0x40:
        GPIO.output(LCD_D6, True)
    if bits&0x80==0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x01==0x01:
        GPIO.output(LCD_D4, True)
    if bits&0x02==0x02:
        GPIO.output(LCD_D5, True)
    if bits&0x04==0x04:
        GPIO.output(LCD_D6, True)
    if bits&0x08==0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

def lcd_toggle_enable():
    time.sleep(0.0005)
    GPIO.output(LCD_E, True)
    time.sleep(0.0005)
    GPIO.output(LCD_E, False)
    time.sleep(0.0005)

def lcd_text(message,line):
 # Send text to display
    message = message.ljust(LCD_CHARS," ")

    lcd_write(line, LCD_CMD)

    for i in range(LCD_CHARS):
        lcd_write(ord(message[i]),LCD_CHR)


#Begin program
try:
    main()
 
except KeyboardInterrupt:
    pass
 
finally:
    lcd_write(0x01, LCD_CMD)
    lcd_text("So long!",LCD_LINE_1)
    GPIO.cleanup()