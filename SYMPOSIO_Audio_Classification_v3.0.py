#Speech     :1
#Eating     :2
#Silence    :3
#Music      :4
#Joy        :5
#Loud       :6

import pyaudio
import librosa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import Patch
from matplotlib.widgets import RadioButtons
#import keras
import os
import time
import math

import yamnet.params as params
import yamnet.yamnet as yamnet_model

from wizControl import *


turnOn(socketA)
turnOn(socketB)
turnOn(socketC)
setBrightness(socketA,100)
setBrightness(socketB,100)
setBrightness(socketC,100)
setTemperature(socketA,100)
setTemperature(socketB,100)
setTemperature(socketC,100)

dirname = os.path.dirname(__file__)

yamnet = yamnet_model.yamnet_frames_model(params)
yamnet.load_weights(os.path.join(dirname, 'yamnet/yamnet.h5'))
yamnet_classes = yamnet_model.class_names(os.path.join(dirname, 'yamnet/yamnet_class_map.csv'))



activeEvents=[1, 1, 1, 1, 1, 1, 6, 1, 1, 6, 6, 6, 1, 5, 5, 5, 5, 5, 5, 6, 6, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 5, 5, 0, 0, 5, 5, 5, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 6, 6, 6, 6, 0, 0, 0, 0]

audio_chunck_duartion=5 #in seconds
frame_len = int(params.SAMPLE_RATE * audio_chunck_duartion) #


p = pyaudio.PyAudio()
update=False
started=False
startTime=0
duration=0
maxDuration=20*60  # Maximum Meal Duration <--------------------------------------------------------
lightColor="#1CC4AF"

def audioCallback(in_data, frame_count, time_info, status):
    global frame_len,cnt,melspec,scores,update
    #print(in_data)     # takes too long in callback
    #global rms
    #rms = audioop.rms(in_data, WIDTH)  # compute audio power
    # # print(rms)  # new # takes too long in callback
    # return in_data, pyaudio.paContinue
    # data read
    
    # byte --> float
    frame_data = librosa.util.buf_to_float(in_data, n_bytes=2, dtype=np.int16)
    # model prediction
    scores, melspec = yamnet.predict(np.reshape(frame_data, [1, -1]), steps=1)
    
    update=True
    return in_data, pyaudio.paContinue

def calculateAverage():
    global eventsAveragePercentage,yamnet_classes,historyLen,eventsShortHistory,SE_ShortHistoryValues,SE_ShortHistoryPercentage
    #Symposio Events
    for i in range(len(SE_ShortHistoryPercentage)):
        SE_ShortHistoryPercentage[i]=0
        for j in range(historyLen):
            SE_ShortHistoryPercentage[i]+=SE_ShortHistoryValues[i][j]
    #print(SE_ShortHistoryPercentage)
    sum=0.00001
    for e in SE_ShortHistoryPercentage:
        sum+=e
    for i in range(len(SE_ShortHistoryPercentage)):
        SE_ShortHistoryPercentage[i]=100*SE_ShortHistoryPercentage[i]/sum
    #print(SE_ShortHistoryPercentage)

def on_key(event):
    global stream,p,plt,client
    if event.key == 'escape':
        plt.close(event.canvas.figure)
        stream.stop_stream()
        stream.close()
        p.terminate()
        exit()
    elif event.key=='b':
        client.send_message("/blink", 5)  
    elif event.key=='s':
        client.send_message("/rgb", [0,255,0])   
    elif event.key=='a':
        client.send_message("/rgb", [255,255,255])   

def close_window(event):
    global stream,p,plt
    plt.close(event.canvas.figure)
    stream.stop_stream()
    stream.close()
    p.terminate()
    exit()

def savePlots(event):
    global plt,dirname
    print("Saving plots")
    plt.savefig(os.path.join(dirname,"saves/save-"+str(time.time())+".png"))

def startDinner(event):
    global started,startTime
    started=True
    startTime=time.time()
    setBrightness(socketA,30)
    setBrightness(socketB,30)
    setBrightness(socketC,30)
    setTemperature(socketA,0)
    setTemperature(socketB,0)
    setTemperature(socketC,0)
    print("Starting Dinner")

def printTime():
    global startTime,duration
    duration=time.time()- startTime
    sec=duration
    sec = sec % (24 * 3600)
    hour = sec // 3600
    sec %= 3600
    min = sec // 60
    sec %= 60
    return "%02d:%02d:%02d" % (hour, min, sec) 

def Kelvin2RGB( temperature,  brightness):
    _red = _green = _blue = 0
    t = temperature * 0.01
    if (t <= 66):
        _red = 255
        _green = (99.4708025861 * math.log(t)) - 161.1195681661
        if (t > 19):
            _blue = (138.5177312231 * math.log(t - 10)) - 305.0447927307
        else:
            _blue = 0
    else:
        _red   = 329.698727446  * math.pow(t - 60, -0.1332047592)
        _green = 288.1221695283 * math.pow(t - 60, -0.0755148492)
        _blue  = 255

    f = 0.01 * brightness

    _red   = clamp(f * _red,0,255)
    _green = clamp(f * _green,0,255)
    _blue  = clamp(f * _blue,0,255)
    return(_red,_green,_blue)

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def setPreset(label):
    global currentPreset
    currentPreset=label
    print(currentPreset)

stream = p.open(format=pyaudio.paInt16,channels=1,rate=params.SAMPLE_RATE,input=True,frames_per_buffer=frame_len,stream_callback=audioCallback)

cnt = 0
stream.start_stream()

totalClasses=len(yamnet_classes)

historyLen=int(60/audio_chunck_duartion) #Time length for calulating average values of symposio events
#eventsShortHistory=[[0]*historyLen for i in range(totalClasses)]
#eventsAveragePercentage=[0]*totalClasses
#eventsTotalHistory=[0]*totalClasses #


SE_Names=["Speech","Eating","Silence","Music","Joy","Loud"] 
symposioEventsColors=['tab:green', 'tab:orange','tab:blue', 'tab:red', 'tab:olive','tab:purple']
SE_CurrentValues=[0]*len(SE_Names) #Current values of syposion events for the current audio chunk
SE_CurrentPercentage=[0]*len(SE_Names)  #SE_CurrentValues converted to percentages
SE_TotalValues=[0]*len(SE_Names) # Symposio events total values for all time 
SE_TotalPercentage=[0]*len(SE_Names) #SE_TotalValues converted to percentages
SE_ShortHistoryValues=[[0]*historyLen for i in range(len(SE_Names))]# Symposio Events values for short history of time (length=historyLen)
SE_ShortHistoryPercentage=[0]*len(SE_Names) #SE_ShortHistoryValues converted to percentages


topCurrentEventsLength=5 #Number of top current events of the last audio chunk
topCurrentEventsNames=[""]*topCurrentEventsLength #Names of top current events of the last audio chunk
topCurrentEventsValues=[0]*topCurrentEventsLength #Values of top current events of the last audio chunk
 
# topTotalEventsLength=20 #Number of top current events of the last audio chunk
# topTotalEventsNames=[""]*topTotalEventsLength
# topTotalEventsPercentage=[0]*topTotalEventsLength

currentPreset="Typical"

plt.rcParams['figure.figsize'] = [15, 8]
plt.rcParams['toolbar'] = 'None'
plt.style.use('dark_background')
#fig, ((ax2, axTotal), (axLight, ax1), (ax5, ax6)) = plt.subplots(3,2)

fig = plt.figure()
fig.tight_layout()
gs = fig.add_gridspec(3,2,height_ratios=[1,1,1],width_ratios =[1,2],wspace=0.1,hspace=0.1)
gs.update(left=0.03,right=0.99,top=0.95,bottom=0.07,wspace=0.1,hspace=0.2)

gs0 = gs[1,1].subgridspec(1, 4, wspace=0.1, hspace=0.1)
gs00 = gs0[0,3].subgridspec(2, 2, wspace=0.1, hspace=0.1)


gsAver = gs[0,1].subgridspec(1, 2, wspace=0.1, hspace=0.1)

axSpect = fig.add_subplot(gsAver[0, 1])
ax2 =  fig.add_subplot(gs[0, 0])
ax2.tick_params(axis="y",direction="in", pad=-10)
axLight = fig.add_subplot(gsAver[0, 0])
#axLight.margins(x=0.001)
axLight.tick_params(
    axis='both',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    left=False,         # ticks along the top edge are off
    labelbottom=False,
    labelleft=False)
axTotal =fig.add_subplot(gs0[0, 0:3])
axAver = fig.add_subplot(gs[1, 0])
axHist = fig.add_subplot(gs[2, :])
axHist.margins(x=0.001)

handle = [
    Patch(facecolor=symposioEventsColors[0], label=SE_Names[0]),
    Patch(facecolor=symposioEventsColors[1], label=SE_Names[1]),
    Patch(facecolor=symposioEventsColors[2], label=SE_Names[2]),
    Patch(facecolor=symposioEventsColors[3], label=SE_Names[3]),
    Patch(facecolor=symposioEventsColors[4], label=SE_Names[4]),
    Patch(facecolor=symposioEventsColors[5], label=SE_Names[5]),
]
axHist.legend(handles=handle,loc='upper left')
axSaveBt = fig.add_subplot(gs00[0, 1])
axStartBt = fig.add_subplot(gs00[0, 0])
axPresets = fig.add_subplot(gs00[1, :])
axPresets.set_facecolor((0.3, 0.3, 0.3))

saveBt = Button(axSaveBt, 'Save Plots',color="0.2")
saveBt.on_clicked(savePlots)
startBt = Button(axStartBt, 'Start',color="0.2")
startBt.on_clicked(startDinner)

presetsRB = RadioButtons(axPresets, ('Typical','Reversed','Conversation','Eating','Single'))
for r in presetsRB.labels: r.set_fontsize(10)
for circle in presetsRB.circles: 
    circle.set_height(0.10)
    circle.set_radius(0.04)

presetsRB.on_clicked(setPreset)

fig.canvas.manager.set_window_title('SYMPOSIO - Audio Classification')
fig.tight_layout(pad=3.0)
plt.ion()
plt.show()


while True:
    if update and started:
        update=False
        prediction = np.mean(scores, axis=0)
        #top_i = np.argsort(prediction)[::-1][:len(prediction)]
        #print('Current event:')
        #found=0

        #Prints Current Events
        #top_i = np.argsort(prediction)[::-1][:topCurrentEventsLength]
        # print('Current event:')
        # for i in top_i:
        #     print(yamnet_classes[i], prediction[i])
        
        #Calulate Top Current Events Array
        print('Current event:')
        top_class_indices = np.argsort(prediction)[::-1][:topCurrentEventsLength]
        n=0
        for i in top_class_indices:
            topCurrentEventsNames[n]=yamnet_classes[i]
            topCurrentEventsValues[n]=prediction[i]
            print(yamnet_classes[i], prediction[i])
            n+=1

            
        #Update Total History , Short History Events and SE_TotalValues and 
        SE_CurrentValues[:len(SE_CurrentValues)] = [0] * len(SE_CurrentValues)
        for i in range(totalClasses):
            #eventsTotalHistory[i]+=prediction[i]
            #eventsShortHistory[i][cnt % historyLen] = prediction[i]
            if activeEvents[i]>0:
                SE_TotalValues[activeEvents[i]-1]+=prediction[i]
                SE_CurrentValues[activeEvents[i]-1]+=prediction[i]
        #Update SE_ShortHistoryValues 
        for i in range(len(SE_CurrentValues)):
            SE_ShortHistoryValues[i][cnt % historyLen] =SE_CurrentValues[i]

        #Convert values to percentages

        totalVal=0.0001+sum(SE_CurrentValues)
        for i in range(len(SE_CurrentValues)):
            SE_CurrentPercentage[i]=100.0*SE_CurrentValues[i]/totalVal
        print("SE_CurrentPercentage")
        print(SE_CurrentPercentage)



        totalVal=0.0001+sum(SE_TotalValues)
        print("SE_TotalValues")
        print(SE_TotalValues)
        for i in range(len(SE_TotalValues)):
            SE_TotalPercentage[i]=100.0*SE_TotalValues[i]/totalVal
        print(SE_TotalPercentage)


        calculateAverage()
        #print(SE_ShortHistoryPercentage)
        #print("------------------------------------")
        #print(SE_ShortHistoryValues)
        #print("------------------------------------")
        
        #PLOTS------------------
        #Spectrogram---------------------
        axSpect.imshow(melspec.T, cmap='jet', aspect='auto', origin='lower')
        axSpect.set_title('Spectrogram')
        
        #plt.rc('xtick', labelsize=8) 
        #Current Audio Events---------------------
        ax2.clear()
        ax2.barh(topCurrentEventsNames[::-1], topCurrentEventsValues[::-1],color=(0,0.4,0.7))
        ax2.set_yticklabels(topCurrentEventsNames[::-1], ha='left')
        ax2.tick_params(axis='y',labelsize=8)
        ax2.grid(axis='x')
        #ax2.set_xlabel('percentage')
        ax2.set_title('Current Audio Events')
        fig.align_labels()

        #SYMPOSIO Events---------------------
        axTotal.clear()
        axTotal.set_title('SYMPOSIO Total Events %')
        axTotal.bar(SE_Names,SE_TotalPercentage,color=symposioEventsColors)
        #axTotal.pie(SE_TotalValues,labels=SE_Names,autopct='%1.0f%%', startangle=0,rotatelabels =True)
        for index, value in enumerate(SE_TotalPercentage):
            axTotal.text(x=index, y=value, s=str("%.1f" % value),ha='center',va='bottom', fontweight='bold')
        #print(SE_Names,SE_TotalValues)
        plt.rcParams['font.size'] = 8

        axAver.clear()
        axAver.set_title('SYMPOSIO Last Events %')
        axAver.bar(SE_Names,SE_ShortHistoryPercentage,color=symposioEventsColors)
        for index, value in enumerate(SE_ShortHistoryPercentage):
            axAver.text(x=index, y=value, s=str("%.1f" % value),ha='center',va='bottom', fontweight='bold')
        plt.rcParams['font.size'] = 8

        #SYMPOSIO Events History---------------------
        bottom=0
        for i in range(len(SE_CurrentPercentage)):
            axHist.bar(cnt,SE_CurrentPercentage[i],width=1.0,bottom=bottom,color=symposioEventsColors[i])
            bottom+=SE_CurrentPercentage[i]
        axHist.set_xlabel(printTime() + " " + str(int(100*duration/maxDuration)) +"% of meal time")


        plt.gcf().canvas.mpl_connect('key_press_event', on_key)

        
        cnt+=1
        if (cnt*audio_chunck_duartion)%10==0:
            savePlots("")

        
        #PRESETS BEGIN----------------------------------------------
        #temp=mapRange(duration,0,maxDuration,0,100)
        #0 Speech     :Cool / -
        #1 Eating     :Warm / Dimm
        #2 Silence    :Warm / Dimm
        #3 Music      :-
        #4 Joy        :Cool / Brightness
        #5 Loud       :Cool / Brightness
        #
        if currentPreset=="Typical" or currentPreset=="Single" or currentPreset=="Conversation" or currentPreset=="Eating":
            bri=mapRange(duration,0,maxDuration,10,60)#40-100
            warm=2*SE_CurrentPercentage[1]+4*SE_CurrentPercentage[2]#2*SE_CurrentPercentage[1]+2*SE_CurrentPercentage[2]
            cool=0.5*SE_CurrentPercentage[0]+2*SE_CurrentPercentage[4]+2*SE_CurrentPercentage[5]
            temp=40*cool/(cool+warm)
            dimFactor=SE_CurrentPercentage[1]+SE_CurrentPercentage[2]
            briFactor=SE_CurrentPercentage[4]+SE_CurrentPercentage[5]+SE_CurrentPercentage[0]
            briPercent=20*briFactor/(dimFactor+briFactor)#30*briFactor/(dimFactor+briFactor)
            bri+=briPercent
            bri=clamp(bri,0,100)
            temp=clamp(temp,0,100)
        elif currentPreset=="Reversed":
            bri=mapRange(duration,0,maxDuration,10,60)#40-100
            cool=2*SE_CurrentPercentage[1]+4*SE_CurrentPercentage[2]#2*SE_CurrentPercentage[1]+2*SE_CurrentPercentage[2]
            warm=0.5*SE_CurrentPercentage[0]+2*SE_CurrentPercentage[4]+2*SE_CurrentPercentage[5]
            temp=40*cool/(cool+warm)
            briFactor=SE_CurrentPercentage[1]+SE_CurrentPercentage[2]
            dimFactor=SE_CurrentPercentage[4]+SE_CurrentPercentage[5]+SE_CurrentPercentage[0]
            briPercent=20*briFactor/(dimFactor+briFactor)#30*briFactor/(dimFactor+briFactor)
            bri+=briPercent
            bri=clamp(bri,0,100)
            temp=clamp(temp,0,100)
        
        speechMaxLimit=80
        speechMinLimit=5
        silenceMaxLimit=60
        eatMinLimit=2
        if currentPreset=="Conversation":
            speechMaxLimit=90
            speechMinLimit=30
            silenceMaxLimit=40
        if currentPreset=="Eating":
            speechMaxLimit=60
            speechMinLimit=3
            silenceMaxLimit=60
            eatMinLimit=3

        #PRESETS END----------------------------------------------
            
        kelvin= int(mapRange(temp,0,100,2700,6500))
        rgb=Kelvin2RGB(kelvin,bri)
        print(rgb)
        #colorsys.hsv_to_rgb(0.13,1.0-temp/100.0,bri/100)
        lightColor='#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))
        #LIGHT COLOR
        axLight.set_facecolor(lightColor)
        axLight.set_title("Temp=" +str(int(temp))+"% Bri="+str(int(bri))+" c="+lightColor)

        print ("Brightness",bri,"Temperature",temp)
        print(cnt,historyLen, cnt%historyLen)

        if cnt%historyLen==0:
            print("Checking...")
            if SE_ShortHistoryPercentage[0]>speechMaxLimit: #Speech
                print("slowBlink...#80% Too much Speech")
                axLight.set_title("slowBlink...#80% Speech")
                slowBlink(bri,temp-50)
            elif SE_ShortHistoryPercentage[2]>silenceMaxLimit and currentPreset!="Eating": #Silence
                print("fastBlink...#60% Too much Silence")
                axLight.set_title("fastBlink...#60% Silence")
                fastBlink(bri,temp+50)
            elif SE_ShortHistoryPercentage[1]<eatMinLimit: #Not Eating
                print("slowBlink...#Not Eating")
                axLight.set_title("slowBlink...#Not Eating")
                slowBlink(bri,temp-50)
            elif SE_ShortHistoryPercentage[0]<speechMinLimit and currentPreset!="Eating": #Not Speaking
                print("fastBlink...#Not Speaking")
                axLight.set_title("fastBlink...#Not Speaking")
                fastBlink(bri,temp+50)
        else:
            setBrightness(socketA,bri)
            setBrightness(socketB,bri)
            setTemperature(socketA,temp)
            setTemperature(socketB,temp)
            if duration<0.9*maxDuration:
                setBrightness(socketC,bri)
                setTemperature(socketC,temp)
            else:
                col=mapRange(duration,0,maxDuration,0,100)
                print("Color=",col)
                setColor(socketC,100,100-col,100,bri+col)
        
        fig.canvas.mpl_connect('close_event', close_window)
        fig.canvas.draw()
        fig.canvas.flush_events()

        if duration>=maxDuration-2*audio_chunck_duartion:
            print("Finished!--------------------")
            markFinish()
            savePlots("")
            started=False




    
    time.sleep(0.01)
    fig.canvas.flush_events()
    
