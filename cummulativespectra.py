'''
PROGRAM FOR READING IN TRIGGER TIMES FROM A TEXT FILE AND PLOTTING
THE TIME SERIES, SPECTROGRAM, AND FT OF THESE TIMES. GIVES AN OPTION
TO SAVE CERTAIN EVENTS TO A NEW TEXT FILE
'''
from numpy import* 
import matplotlib.pyplot as plt
from obspy import UTCDateTime
from obspy.fdsn import Client
from obspy import Stream
from obspy import Trace
import obspy.signal
from obspy.xseed import Parser
from obspy.signal import PPSD
import numpy as np
import matplotlib.pyplot as plt
from petfun import*

def RealMultiTaperList(trlist): #Input: list of traces;  Output: freq and amplitude arrays
    freq,amp=RealMultiTaper(trlist[0])
    freqarray=freq
    numamp=len(amp)+1000 # = length of padded amplitude array
    amparray=np.linspace(0,0,numamp)
    
    for tr in trlist:
        print('doing multi-taper')
        freq,amp=RealMultiTaper(tr)
        amp=np.lib.pad(amp,(0,numamp-len(amp)),'constant',constant_values=(0,0))
        amparray+=np.array(amp)
    amparray=amparray[:len(freqarray)]
    return freqarray,amparray

def Freq2Per(freq,amp): #Input: freqs (assume freq[0]=0), amps;  Output: periods, amps
    freq=freq[:0:-1]
    per=np.divide(1,freq)
    amp=amp[:0:-1]
    return per,amp

#FREQUENTLY CHANGED SETTINGS
pickfile='picks_stalta_Jan/ShortDurLocalLowCorr'
bandfreq=[.1,45]
maxplotfreq=40 #max freq plotted

#OTHER SETTINGS
station='WIZ'
channel='Z'
windowtime=3*60.000
delaytime=20.000
buffer=120.000 #needs to be a few minutes so that small changes in the FFT between samples don't cause errors
#noise1=['2014-01-12T00:03:00']
#LowFreqEvent=['2014-08-06T04:21:00']

#Choose Triggers or Noise
#picksUTC=LogTime2UTC(LowFreqEvent)
picksUTC = ReadTriggers(pickfile)


##################################
#MY METHOD FOR CUMMULATIVE SPECTRA
##################################
trlist=[]
for pick in picksUTC:
    print('getting stream')
    st=GetProcessStreamJava(station,channel,pick-buffer,windowtime+buffer)
    st.slice(pick-delaytime,pick+windowtime-delaytime)
    trlist.append(st[0])

#freq1,amp1=RealMultiTaper(trlist[0])
#freq2,amp2=RealMultiTaper(trlist[1])

freq1,amp1=RealMultiTaperList(trlist)
per2,amp2=Freq2Per(freq1,amp1)


plt.semilogy(freq1,amp1) #plot FFT
#plt.loglog(per2,amp2) #plot FFT
#plt.xticks(np.arange(0,maxplotfreq+1,2))
plt.show()

'''
####################################
#PPSD FROM OBSPY CUMMULATIVE SPECTRA
####################################
trlist2=[]
for i in range(0,len(triggersUTC)):
    print('getting stream')
    st=GetStreamJava(station,channel,triggersUTC[i]-buffer,windowtime+buffer)
    st.slice(triggersUTC[i]-delaytime,triggersUTC[i]+windowtime-delaytime)
    trlist2.append(st[0])

bigtr=trlist2[0]
for tr in trlist2:
    bigtr+=tr
bigtrlist=[bigtr]

paz,waterlevel=StationSpecs(station,channel)

ppsd=PPSDList(trlist2,paz,180) #Inputing either bigtrlist or trlist2 should give same result
ppsd.plot()
'''
