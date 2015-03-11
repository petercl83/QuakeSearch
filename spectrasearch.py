'''
SEARCHES THROUGH DOWNLOADED DATA FOR EVENTS BASED ON SIMILARITY OF SPECTRA
'''
from obspy import UTCDateTime
from obspy import Stream
from obspy import Trace
from obspy.fdsn import Client
from obspy.core import read
import obspy.signal
import numpy as np
import matplotlib.pyplot as plt
import shlex,subprocess
from petfun import*

writefile='triggerLowFreq.057'
downloaddays=1 #Number days downloaded in a single SAC file
numdownloads=90 #Total number of SAC files downloaded
deltat=[300,275] #Window length in seconds for template/sample
advanceby=150 #Number of seconds to advance sliding sample window by
cycles=int((downloaddays*24*60*60-deltat[1])/advanceby)+1
bandFreq=[1,50]
corrFreq=[1,50]
station="WIZ"
channel="Z"

#Input for Reference Window
reftimesUTC=ReadTriggersFromFile('triggers_2014/AugOctLongDur')
refUTC=reftimesUTC[0]
refst=ProcessStream(GetStream(station,channel,refUTC,deltat[0]),station,channel,bandFreq)
reftr=refst[0]

#Start time for quake search
startUTC=UTCDateTime(2014,1,1,9,0,0)
#startUTC=reftimesUTC[0]

'''
#Input for FDSN
swarmUTC=['2014-08-28T17:42:52L12:00','2014-08-28T10:03:48+12:00','2014-08-28T09:25:43+12:00','2014-08-28T09:29:04+12:00','2014-08-28T09:55:12+12:00','2014-08-28T19:48:23+12:00','2014-08-28T10:18:28+12:00']
starttime=UTCDateTime(swarmUTC[0])-2400
endtime=starttime+24*60**2
#starttime=UTCDateTime(2014,1,1,0,0)
#endtime=UTCDateTime(2014,1,10,0,0)
reftime=UTCDateTime(2014,2,1,0,0,0)
numdownloads=int((endtime-starttime)/(24*60**2*downloaddays))
refst=GetStreamFDSN(station,channel,reftime,deltat[0]).slice(reftime,reftime+deltat[0])
'''

SACtime=startUTC
for i in range(0,numdownloads):
    print('Starting new cycle...')
    sampletime=SACtime
    st=GetStream(station,channel,SACtime,downloaddays*24*60**2)    
    for j in range(0,cycles):
        teststUn=st.copy().slice(sampletime,sampletime+deltat[1])
        testst=ProcessStream(teststUn,station,channel,bandFreq)
        testtr=testst[0]
        freq,fftrace1,fftrace2,productTrace,corvalue=CorrelateData(reftr.copy(),testtr.copy(),corrFreq)
        print(sampletime, corvalue)
        #reftr.plot()
        #fftrace1.plot()
        #testtr.plot()
        #fftrace2.plot()
        #productTrace.plot()
        if corvalue > .057:
            print('Earthquake!')
            #fftrace1.plot()
            testtr.plot()
            fftrace2.plot()
            #productTrace.plot()
            logtimes=UTC2LogTime([sampletime])
            WriteTriggers(logtimes,writefile)
        sampletime=sampletime+advanceby
    SACtime=SACtime+downloaddays*24*60**2

'''
#Test Code
st=GetStreamFDSN(station,channel,starttime,downloaddays*24*60**2)
testst=st.copy().slice(sampletime,sampletime+deltat)

st1=refst.copy() #remove
st2=testst.copy() #remove

tr1, freq1, fft1=ProcessData(st1)
tr2, freq2, fft2=ProcessData(st2)
product=CreateTrace(freq1, fft1.data*fft2.data)
st3=Stream(traces=[tr1,tr2])
fft=Stream(traces=[fft1,fft2,product])
fftproduct=Stream(traces=[product])
corvalue=fftproduct.copy().integrate().max()
'''
'''
PlotStream(st3)
PlotStream(fft)
print(corvalue)
    #print(corvalue[0])
    #PlotStream(tr3)
    #PlotStream(fft)

    
'''


'''
#Triggering
cft = classicSTALTA(trace.data, int(5 * df), int(10 * df))
plotTrigger(trace, cft, 1.5, 0.5)
'''
