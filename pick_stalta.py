# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 11:17:23 2014
THIS PROGRAM USES THE STALTA PROGRAM TO SEARCHE THROUGH DOWNLOADED
SEISMIC DATA AND WRITE TRIGGER TIMES TO A TEXT FILE
@author: plin976
"""
from obspy import UTCDateTime
from obspy import Stream
from obspy import Trace
import obspy.signal
from petfun import*

#CHANGABLE SETTINGS
startUTC=UTCDateTime(2014,2,14,4,17,45) #CHECK
#startUTC=UTCDateTime(2014,1,31,1,15,49) #CHECK
#startUTC=UTCDateTime(2014,1,1,16,0,0) #very long Dur teleseismic
#startUTC=UTCDateTime(2014,8,27,10,25,0) #MedDur/LowFreq
#startUTC=UTCDateTime(2014,8,6,4,10,0) #LongDur/LowFreq
#startUTC=UTCDateTime(2014,1,2,1,0,0) #Two ShortDur, closely spaced quakes
plot='n' #y/n
downloadhours=1 #Normal is 1
cycles=24*60

S=1.5   #Tsta, long-->fewer picks at beginning of .sac file
L=150   #Tlta, default 150, must be long to pick up fluid quakes
shortdurfile='Pick_Short_2014-1' #short duration trigger file
longdurfile='Pick_Long_2014-1' #long duration trigger file
T='5'   #Trigger ratio
D='1.5'   #Detrigger ratio
F='300'   #Trigdsensetime, 50 default, doesn't seem to matter much
P='40'   #Trigduration, must >=50 so that one LongDur quake does not show up as multiple picks
Cutoff=60   #Cutoff for short/long duration, must be >P
station='WIZ'
channel='Z'

def FindTriggers(stream3,startUTC,S,L,T,D,F,P): #Input: str, startUTC,trigger/detrigger threshholdd  Output: triggertimes in year:month:day:your:minute:second format
    triggertimesYMD=[]
    triggerdurationsfloat=[]
    stream3.write('stalta.sac',format='SAC') #Writes sac file
    if plot=='y':
        main(["programstalta.py","-S",str(S),"-L",str(L),"-T",T,"-D",D,"-F",F,"-P",P,"-p","-w","peterlog",'stalta.sac']) ##run stalta program which writes logfile
    else:
        main(["programstalta.py","-S",str(S),"-L",str(L),"-T",T,"-D",D,"-F",F,"-P",P,"-w","peterlog",'stalta.sac']) ##run stalta program which writes logfile
    subprocess.call('rm stalta.sac', shell=True)
    triggertimes,triggerdurations=ReadTriggerLog('peterlog')

    print("LISTS",triggertimes,triggerdurations)

    if triggertimes!=[]:
        for i in range(0,len(triggertimes)):
            year=str(startUTC.year)
            month=str(startUTC.month)
            day=str(startUTC.day)
            if len(month)==1:
                month='0'+month
            if len(day)==1:
                day='0'+day
            triggertimesYMD.append(year+'-'+month+'-'+day+'T'+triggertimes[i])
            triggerdurationsfloat.append(float(triggerdurations[i]))
    return triggertimesYMD,triggerdurationsfloat

def ReadTriggerLog(filename): #Input: filename of stalta program log file;   Output: list of triggertimes (H:M:S)
    ref=open(filename,'r')
    linesskipped=13
    for i in range(0,linesskipped):
        ref.readline()
    entries=ref.read().split()
    ref.close()
    eventnum=(len(entries)-25)/16
    triggertimes=[]
    triggerdurations=[]
    for i in range(0,eventnum):
        triggertimes.append(entries[5+16*i])
        triggerdurations.append(entries[10+16*i])
    return triggertimes,triggerdurations
    

j=0
for i in range(0,cycles):
    logtimes=[]
    sampleUTC=startUTC+j*60**2*downloadhours
    try: stream=GetProcessStreamJava(station,channel,sampleUTC-L,downloadhours*60**2+L) #StaLta doesn't start until t>L
    except:
        print('Could not load data!')
    if stream!=0:
        stream.detrend()
        logtimes,durations=FindTriggers(stream,sampleUTC,S,L,T,D,F,P)
        print(logtimes,durations)
        for i in range(0,len(logtimes)):
            if durations[i]<=Cutoff:
                WriteTriggers([logtimes[i]],shortdurfile)
            else:
                WriteTriggers([logtimes[i]],longdurfile)
        j+=1
