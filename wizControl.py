import socket
import time
import json

LightA_IP = "192.168.1.116"
LightB_IP = "192.168.1.117"
CenterLight_IP="192.168.1.115"
MIN_TEMPERATURE=2700
MAX_TEMPERATURE=6500
TIME_DELAY=0.1

#tempH = """{"method":"setPilot","params":{"state":true,"temp":3000}}"""
#tempC = """{"method":"setPilot","params":{"state":true,"temp":6000}}"""
#bri = """{"method":"setPilot","params":{"state":true,"dimming":100}}"""
# """{"id":1,"method":"setPilot","params":{"temp":2200,"dimming":80}}"""
# """{"params":{"orig":"andr","temp":3000,"dimming",80},"id":6,"method":"setPilot"}"""
#"""{"id":1,"method":"setPilot","params":{"temp":2200,"dimming":80}}"""
socketA = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketA.connect((LightA_IP, 38899))
socketB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketB.connect((LightB_IP, 38899))
socketC = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketC.connect((CenterLight_IP, 38899))

def clamp(value,minVal,maxVal):
    v=value
    if v<minVal:
        v=minVal
    if v>maxVal:
        v=maxVal
    return v

def mapRange(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

def turnOn(bulb):
    print("Turning ON light")
    cmd = """{"id":1,"method":"setState","params":{"state":true}}"""
    bulb.sendall(bytes(cmd, "utf-8"))
    time.sleep(TIME_DELAY)

def turnOff(bulb):
    print("Turning OFF light")
    cmd = """{"params":{"orig":"andr","state":false},"id":6,"method":"setPilot"}"""
    bulb.sendall(bytes(cmd, "utf-8"))
    time.sleep(TIME_DELAY)

def setBrightness(bulb,b):
    """
    socketA or socketA for bulb and from 10 to 100 for Brightness
    """
    #print("Setting Brightness to "+str(b))
    b=clamp(b,10,100);
    cmd = """{"method":"setPilot","params":{"state":true,"dimming":"""+str(b)+"""}}"""
    bulb.sendall(bytes(cmd, "utf-8"))
    time.sleep(TIME_DELAY)

def setTemperature(bulb,t):
    #from 0 to 100, 0 for warm and 100 for cool
    """
    socketA or socketA for bulb and from 0 to 100, 0 for Warm and 100 for Cool
    """
    if t<0:
        t=0
    if t>100:
        t=100
    temp=mapRange(t,0,100,MIN_TEMPERATURE,MAX_TEMPERATURE)
    print("Setting Temperature to " +str(t) +"% " +str(temp)+"K")
    cmd = """{"method":"setPilot","params":{"state":true,"temp":"""+str(temp)+"""}}"""
    bulb.sendall(bytes(cmd, "utf-8"))
    time.sleep(TIME_DELAY)

def markFinish():
    print("Playing Finish Light Animation")
    setTemperature(socketA,50)
    setTemperature(socketB,50)

    for i in range(5):
        setBrightness(socketA,10)
        setBrightness(socketB,100)
        setColor(socketC,100,0,100,100)
        time.sleep(0.5)
        setBrightness(socketA,100)
        setBrightness(socketB,10)
        setColor(socketC,0,50,100,100)
        time.sleep(0.5)

    setBrightness(socketA,100)
    setBrightness(socketB,100)
    setColor(socketC,100,0,100,100)

def fastBlink(bri,temp):
    bri=clamp(bri,60,100)
    temp=clamp(temp,0,100)
    print("Fast Blink ",bri,temp)
    #origTemp_A,origBri_A=getState(socketA)
    origTemp_B,origBri_B=getState(socketB)
    origTemp_C=origTemp_B
    origBri_C=origBri_B

    #setTemperature(socketA,temp)
    setTemperature(socketB,temp)
    #setTemperature(socketC,temp)
    for i in range(3):
        #setBrightness(socketA,0)
        setBrightness(socketB,0)
        setBrightness(socketC,0)
        #setColor(socketC,0,0,0,100)
        time.sleep(0.5)
        #setBrightness(socketA,bri)
        setBrightness(socketB,bri)
        #setBrightness(socketC,bri)
        setColor(socketC,0,45,100,bri)
        time.sleep(0.5)

    #setTemperature(socketA,origTemp_A)
    setTemperature(socketB,origTemp_B)
    setTemperature(socketC,origTemp_C)
    #setBrightness(socketA,origBri_A)
    setBrightness(socketB,origBri_B)
    setBrightness(socketC,origBri_C)
    
def slowBlink(bri,temp):
    bri=clamp(bri,60,100)
    temp=clamp(temp,0,100)
    print("Slow Blink ",bri,temp)
    origTemp_A,origBri_A=getState(socketA)
    #origTemp_B,origBri_B=getState(socketB)
    origTemp_C=origTemp_A
    origBri_C=origBri_A

    setTemperature(socketA,temp)
    #setTemperature(socketB,temp)
    #setTemperature(socketC,temp)
    setColor(socketC,100,15,0,bri)
    for i in range(2):
        steps=10
        for j in range(steps):
            setBrightness(socketA,(1.0-j/steps)*bri)
            #setBrightness(socketB,(1.0-j/steps)*bri)
            #setBrightness(socketC,(1.0-j/steps)*bri)
            setColor(socketC,(1.0-j/steps)*100,(1.0-j/steps)*15,0,bri)
        for j in range(steps):
            setBrightness(socketA,j/steps*bri)
            #setBrightness(socketB,j/steps*bri)
            #setBrightness(socketC,j/steps*bri)
            setColor(socketC,j/steps*100,j/steps*15,0,bri)
            #time.sleep(0.1)
    
    setTemperature(socketA,origTemp_A)
    #setTemperature(socketB,origTemp_B)
    setTemperature(socketC,origTemp_C)
    setBrightness(socketA,origBri_A)
    #setBrightness(socketB,origBri_B)
    setBrightness(socketC,origBri_C)

def getState(bulb):
    empty_socket(bulb)
    cmd = """{"method":"getPilot","params":{}}"""
    bulb.sendall(bytes(cmd, "utf-8"))
    data = bulb.recv(4096) 
    #print(data)
    res = json.loads(data)
    bri=res["result"]["dimming"]
    try:
        temp=res["result"]["temp"]
    except:
        temp=5000
    temp=mapRange(temp,MIN_TEMPERATURE,MAX_TEMPERATURE,0,100)
    return (temp,bri)

def empty_socket(sock):
    sock.setblocking(0)
    while True:
        try:
            sock.recv(1024)
        except BlockingIOError:
            sock.setblocking(1)
            return

def setColor(bulb,r,g,b,bri):
     #from r,g,b from 0 to 100, and bri from 0 to 100
    bri=clamp(bri,10,100);

    """
    socketA or socketA for bulb and from 0 to 100, 0 for Warm and 100 for Cool
    """
    print("Setting Color to " +str(r) +","+str(g) +","+str(b) +" " +str(bri)+"%")
    cmd = """{"method":"setPilot","params":{"r":"""+str(r)+""","g":"""+str(g)+""","b":"""+str(b)+""","dimming":"""+str(bri)+"""}}"""
    bulb.sendall(bytes(cmd, "utf-8"))
    time.sleep(TIME_DELAY)

# setTemperature(socketC,0)
# time.sleep(2)
#setColor(socketC,100,0,100,100)
# time.sleep(2)
# setColor(socketC,100,0,0,50)
# time.sleep(2)
# setColor(socketC,0,0,100,100)
# time.sleep(2)
# setColor(socketC,100,00,100,100)
# time.sleep(2)
#setTemperature(socketC,0)
#markFinish()
#slowBlink(50,50)
#fastBlink(50,50)
