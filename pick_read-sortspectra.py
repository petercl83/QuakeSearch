from numpy import* 
from obspy import UTCDateTime
from obspy import Stream
from obspy import Trace
import obspy.signal
from petfun import*

'''
#PROGRAM FOR READING A FILE OF PICKTIMES AND SELECTING OUT THOSE TIMES
#WHICH MATCH A SPECTRA TEMPLATE
'''

#CHANGEABLE SETTINGS
pickfile='picks_stalta_Jan/ShortDurLocal' #Raw pick times
highcorrfile='picks_stalta_Jan/ShortDurHighCorr' #file to write high-correlated quakes to
lowcorrfile='picks_stalta_Jan/ShortDurLowCorr' #file to write low-correlated quakes to
bandfreq=[1,45]
corvaluethreshold=.088 #minimum correlation value for a high-correlated quake

#DOWNLOAD REFERENCE WINDOW
station="WIZ"
channel="Z"
windowtimes=[200,180] #The first # is the window time for the refererence, the second is the window time for the teststream (should be shorter)
reftime=UTCDateTime(2014,8,6,4,21,0)
refst=GetProcessStreamJava(station,channel,reftime,windowtimes[0])
reftr=refst[0]
#reftr.data=obspy.signal.highpass(reftr.data,5,df=reftr.stats.sampling_rate,corners=1)

#GET LIST OF TRIGGER TIMES (UTC)
ref=open(pickfile,'r')
picktimes=ref.readlines()
picksUTC=LogTime2UTC(picktimes)
ref.close()

'''
#A LIST OF EARTHQUAKES TO TEST SCRIPT
triggersUTC=[]
swarmUTC=['2014-08-28T17:42:52+12:00','2014-08-28T10:03:48+12:00','2014-08-28T09:25:43+12:00','2014-08-28T09:29:04+12:00','2014-08-28T09:55:12+12:00','2014-08-28T19:48:23+12:00','2014-08-28T10:18:28+12:00']
for i in range(0,len(swarmUTC)):
    triggersUTC.append(UTCDateTime(swarmUTC[i]))
'''

for pick in picksUTC:

    testst=GetProcessStream(station,channel,pick-10,windowtimes[1])
    testtr=testst[0]

    testtr.plot()
    reftr.plot()
    freq, fftref, ffttest, product, corvalue=CorrelateData(reftr.copy(),testtr.copy(),bandfreq)
    ffttest.plot()
    fftref.plot()

    print("Correlation Value:")
    print(corvalue)
    logtimes=UTC2LogTime([pick])
    if corvalue > corvaluethreshold: #corvalue<.0165m
        WriteTriggers(logtimes,highcorrfile)
    else:
        WriteTriggers(logtimes,lowcorrfile)
