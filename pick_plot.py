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
from petfun import*


#Frequently Changed Settings
bandfreq=[.5,40]
maxplotfreq=40 #max freq plotted
triggerfile='picks_spect_2014_90days/LowFreq-.055'
writefile='dummy'

#Other Settings
stations=['WIZ']
channel='Z'
windowtime=6*60
delaytime=10
noise1=['2014-01-12T00:03:00']
noise2=['2014-08-06T04:20:04']
meteor=['2015-02-11T09:55:00']
LowFreqEvent=['2014-08-06T04:20:52']

#Choose Triggers or Noise
#triggersUTC=LogTime2UTC(noise2)
triggersUTC = ReadTriggers(triggerfile)

st2Co=AllPlotsList(triggersUTC,windowtime,delaytime,bandfreq,maxplotfreq,stations,channel)
