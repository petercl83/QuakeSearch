from obspy import UTCDateTime
from obspy import Stream
from obspy import Trace
from obspy.fdsn import Client
from obspy.core import read
from obspy.signal import PPSD
from obspy.signal.invsim import seisSim
import obspy.signal
import numpy as np
import matplotlib.pyplot as plt
import shlex,subprocess
import sys, os
import nitime.algorithms as tsa
import nitime.utils as utils
import obspy.neries as ne
from nitime.viz import winspect
from nitime.viz import plot_spectral_estimate


lib_path=os.path.abspath('stalta_v.3.80')
sys.path.append(lib_path)
from programstalta import*



#########################
#DOWNLOADING SEISMIC DATA
#########################

def GetProcessStreamFDSN(station,channel,startUTC,deltat,bandFreq=[.1,45],normfactor=1): #Ouput: corrected, bandpassed stream
    stUn=GetStreamFDSN(station,channel,startUTC,deltat)
    stCo=ProcessStreamFDSN(stUn.copy(),station,channel,bandFreq,normfactor)
    return stCo

def GetProcessStreamJava(station,channel,startUTC,deltat,bandFreq=[.1,45],normfactor=1): #Ouput: corrected, bandpassed stream
    stUn=GetStreamJava(station,channel,startUTC,deltat)
    stCo=ProcessStreamJava(stUn.copy(),station,channel,bandFreq,normfactor)
    return stCo

def ProcessStreamFDSN(st,station,channel,bandFreq,normfactor=1,pre_filt = (.05,.5, 49.0, 50.0)): #Input: Uncorrected Stream, Output: Corrected (using FDSN), bandpassed stream
    st.detrend('constant')
    paz,waterlevel=StationSpecs(station,channel)
    print('WATER LEVEL:',waterlevel)
    st.remove_response(water_level=waterlevel, output='DISP', pre_filt=pre_filt).detrend('constant') #Water level must be low to match the Java ouput
    for i in range(0,len(st)):
        st[i].data=obspy.signal.bandpass(st[i].data,bandFreq[0],bandFreq[1],df=st[i].stats.sampling_rate,corners=4)/normfactor
    st.detrend('constant')
    return st

def ProcessStreamJava(st,station,channel,bandFreq,normfactor=1,pre_filt = (.05,.5, 49.0, 50.0)): #Input: Uncorrected Stream, Output: bandpassed, corrected stream
    st.detrend('constant')
    st=CorrectInstrumentWaterLevel(st.copy(),station,channel,pre_filt) #.detrend('constant') #correct trace
    for i in range(0,len(st)):
        st[i].data=obspy.signal.bandpass(st[i].data,bandFreq[0],bandFreq[1],df=st[i].stats.sampling_rate,corners=4)/normfactor
    st.detrend('constant')
    return st

def GetProcessStream(station,channel,startUTC,deltat,bandFreq=[.1,45],normfactor=1): #Gets stream from FDSN or Java (whichever works)
    st=GetStreamFDSN(station,channel,startUTC,deltat)
    if st==0:
        print("FDSN didn't work.  Trying Java...")
        st=GetStreamJava(station,channel,startUTC,deltat)
    stCo=ProcessStreamJava(st.copy(),station,channel,bandFreq,normfactor)
    return stCo

def GetStreamFDSN(station,channel,startUTC,deltat): #Gets a stream via FDSN
    endUTC=startUTC+deltat
    fdsn_client=Client(base_url="http://service.geonet.org.nz")
    try: stream=fdsn_client.get_waveforms("NZ",station,"10","HH"+channel,startUTC,endUTC,attach_response=True)
    except:
        print('FDSN SERVICE APPEARS TO BE DOWN')
        stream=0
    return stream

def GetStreamJava(station,channel,startUTC,deltat): #Gets stream using a Java applet from Geonet
    starttime=UTCtoJava(startUTC)
    if len(station)==3:
        try:
            subprocess.call('java -jar GeoNetCWBQuery-4.2.0-bin.jar -s "NZ'+station+'  HH'+channel+'10" -b "'+starttime+'" -d '+str(deltat)+' -t sac', shell=True)
        except:
            print('JAVA SERVICE APPEARS TO BE DOWN')
            stream=0
        else:
            filename='NZ'+station+'__HH'+channel+'10.sac'
            stream=read(filename, format='SAC')
            subprocess.call('rm '+filename, shell=True)
    if len(station)==4:
        try:
            subprocess.call('java -jar GeoNetCWBQuery-4.2.0-bin.jar -s "NZ'+station+' HH'+channel+'10" -b "'+starttime+'" -d '+str(deltat)+' -t sac', shell=True)
        except:
            print('JAVA SERVICE APPEARS TO BE DOWN')
            stream=0
        else:
            filename='NZ'+station+'_HH'+channel+'10.sac'
            stream=read(filename, format="SAC")
            subprocess.call('rm '+filename, shell=True)
    return stream

def GetSacFileJava(station,channel,startUTC,deltat): #Ouput: writes sac file and returns file name
    starttime=UTCtoJava(startUTC)
    if len(station)==3:
        subprocess.call('java -jar GeoNetCWBQuery-4.2.0-bin.jar -s "NZ'+station+'  HH'+channel+'10" -b "'+starttime+'" -d '+str(deltat)+' -t sac', shell=True)
        filename='NZ'+station+'__HH'+channel+'10.sac'
    if len(station)==4:
        subprocess.call('java -jar GeoNetCWBQuery-4.2.0-bin.jar -s "NZ'+station+' HH'+channel+'10" -b "'+starttime+'" -d '+str(deltat)+' -t sac', shell=True)
        filename='NZ'+station+'_HH'+channel+'10.sac'
    return filename

######################
#INSTRUMENT CORRECTION
######################
def CorrectInstrument(st,station='WIZ',channel='Z',pre_filt = (.05,.5, 49.0, 50.0)):
    polesandzeros,waterlevel=StationSpecs(station,channel)
    for i in range(0,len(st)):
       st[i]=st[i].simulate(paz_remove=polesandzeros).detrend('constant')
    return st

def CorrectInstrumentWaterLevel(st,station,channel,pre_filt = (.05,.5, 49.0, 50.0)):
    polesandzeros,waterlevel=StationSpecs(station,channel)
    copy=st.copy()
    for i in range(0,len(st)):
        print('WATER LEVEL:', waterlevel)
        st[i].data=seisSim(data=st[i].data,samp_rate=st[i].stats.sampling_rate,paz_remove=polesandzeros,water_level=waterlevel,pre_filt=pre_filt)
    return st

def StationSpecs(station,channel): #Output: Poles and Zeros
    if station=='WIZ' and  channel=='Z':
        polesandzeros = {
            'poles': [-1.178e-2 + 1.178e-2j, -1.178e-2 - 1.178e-2j, -1.8e+2 + 0j,
                      -1.6e+2 + 0j, -8e1 + 0j],
            'zeros': [0j, 0j],
            'gain': 2000,
            'sensitivity': 8.38861e8} #Either 8.38861e8 or 419430.00 (which??)
        waterlevel = .01

    if station=='WSRZ' and  channel=='Z':
        polesandzeros = {
            'poles': [-1.178e-2 + 1.178e-2j, -1.178e-2 - 1.178e-2j, -1.8e+2 + 0j,
                      -1.6e+2 + 0j, -8e1 + 0j],
            'zeros': [0j, 0j],
            'gain': 2000,
            'sensitivity': 8.38861e13} #Changed this to make PPSD plot on the darn axis
        waterlevel = .01
    return polesandzeros, waterlevel


##########################
#STREAM/TRACE MANIPULATION
##########################

def Normalize(x,y,startx,endx): #Input x,y,startx,endx   Return: sliced x, normalized y
    tr=CreateTrace(x,y)
    t=tr.stats.starttime
    tr2=tr.slice(t+startx,t+endx)
    tr2.data=tr2.data/(tr2.integrate().max())
    returnX = np.linspace(startx,endx,len(tr2.data))
    return returnX, tr2.data
     
def CreateTrace(freq,data):        
    trace = Trace()
    trace.data = data
    trace.stats.sampling_rate = (len(freq)-1)/freq[len(freq)-1]
    return trace

def Envelope(tr):
    tr.filter('bandpass', freqmin=0, freqmax=1, corners=2, zerophase=True)
    envelope = obspy.signal.filter.envelope(tr.data)
    return envelope


####################
#MY SPECTRA ROUTINES
####################

def PPSDList(trlist,paz,ppsd_length): #Input: list of uncorrected traces;  Output: freq and amp arrays
    ppsd=PPSD(trlist[0].stats,paz,ppsd_length=ppsd_length)
    for tr in trlist:
        ppsd.add(tr)
    return ppsd

def RealMultiTaper(tr): #Input: trace, Output: freq, amp
    freq, amp, nu = tsa.multi_taper_psd(tr.data,adaptive=False,jackknife=False)
    freq=(freq/np.pi)*tr.stats.sampling_rate/2
    return freq, amp

def RealFFT(tr): #Input: trace,    output: freq, amp
    #tr.taper('hamming')
    t = np.arange(0, tr.stats.npts / tr.stats.sampling_rate, tr.stats.delta)
    sp = np.fft.rfft(tr.data)
    freq = np.fft.rfftfreq(t.shape[-1],1/tr.stats.sampling_rate) 
    return freq, abs(sp)

##########################
#MY CROSS CORRELATION CODE
##########################
def ProcessData(tr,bandFreq): #input:trace,  output:freq list and normalized and smoothed FFT trace
    freq,amp=RealFFT(tr)
    fftrace=CreateTrace(freq,amp)
    t=fftrace.stats.starttime
    fftrace2=fftrace.slice(t+bandFreq[0],t+bandFreq[1])
    envelope=Envelope(fftrace2)
    fftrace3=CreateTrace(freq,envelope)
    fftrace3.data=fftrace2.data/(fftrace2.integrate().max()) #normalize
    return freq, fftrace3

def CorrelateData(tr1,tr2,bandFreq): #Inpuyt: traces, bandpassed frequencies, Output: freq list, smoothed FFTs and their product (traces), and correlation value (integral of product trace)
    freq1, fftrace1=ProcessData(tr1,bandFreq)
    freq2, fftrace2=ProcessData(tr2,bandFreq)
    productdata=np.lib.pad(fftrace2.data,(0,len(fftrace1.data)-len(fftrace2.data)),'constant',constant_values=(0,0))
    productTrace=CreateTrace(freq1, fftrace1.data*productdata)
    corvalue=productTrace.copy().integrate().max()
    return freq1, fftrace1, fftrace2, productTrace, corvalue

##############
#PLOTTING DATA
##############
def AllPlotsList(triggersUTC,windowtime=180,delaytime=30,bandfreq=[.2,40],maxplotfreq=50,stations=['WIZ'],channel='Z'):
    testst=0
    for i in range(0,len(triggersUTC)):
        for station in stations:
            print(triggersUTC[i])
            #Plot using Java utilities  
            st1Co=GetProcessStreamJava(station,channel,triggersUTC[i]-delaytime,windowtime,bandfreq)
            tr1=st1Co[0]        
            print('DATA FROM JAVA APPLET')
            AllPlots(tr1,maxplotfreq)
            
            '''
            #Plot using FDSN
            st2Co=GetProcessStreamFDSN(station,channel,triggersUTC[i]-delaytime,windowtime,bandfreq)
            tr2=st2Co[0]
            print('DATA FROM FDSN')
            AllPlots(tr2,maxplotfreq)
            
            if raw_input("Keep Quake? (y/n) ")=='y':
            logtimes=UTC2LogTime([triggerUTC[i]])
            WriteTriggers(logtimes,writefile)
            #if raw_input("Write to sac file? (y/n) ")=='y':
            #filename=GetSacFileJava(station,channel,triggersUTC[i]-180,windowtime) #filename dummy
            '''

def AllPlots(tr,maxfreq): #Input: trace, max plotted freq, Output: Time Series, Spectrogram, FT
    freq,amp=RealMultiTaper(tr) #get unsmoothed FFT

    deltafreq=(freq[len(freq)-1]-freq[0])/len(freq)
    freqmaxnum=maxfreq/deltafreq

    tr.plot(number_of_ticks=6) #plot time series
    tr.spectrogram(log=True)
    plt.plot(freq[0:freqmaxnum],amp[0:freqmaxnum]) #plot FFT
    plt.xticks(np.arange(0,maxfreq+1,2))
    plt.show()

def PlotStream(st): #Plots a stream (multiple traces)
    st.sort(['starttime']) #Sort by start time.  This each trace for a single even by start time, which is necessary for plotting the data if you don't plot using obspy.
    dt=st[0].stats.starttime.timestamp
    f, axarr=plt.subplots(len(st))
    for j in range(0,len(st)):
        t2=np.linspace(st[j].stats.starttime.timestamp-dt, st[j].stats.endtime.timestamp-dt, st[j].stats.npts)
        axarr[j].plot(t2,st[j].data,'k')

def PlotTrace(tr):
    dt=tr.stats.starttime.timestamp
    t=np.arange(0,tr.stats.npts/tr.stats.sampling_rate,tr.stats.delta)
    plt.plot(t,tr.data,'k')

#################
#TIME CONVERSIONS
#################

def UTCtoJava(UTC): #Converts UTC time to time string format that is read by Java applet
    month=str(UTC.month)
    day=str(UTC.day)
    hour=str(UTC.hour)
    minute=str(UTC.minute)    
    second=str(UTC.second)    
    if len(month)==1:
        month='0'+month
    if len(day)==1:
        day='0'+day
    if len(minute)==1:
        minute='0'+minute
    if len(second)==1:
        second='0'+second
    JavaTime=str(UTC.year)+'/'+month+'/'+day+' '+hour+':'+minute+':'+second
    return JavaTime

def LogTime2UTC(times): #Input: list of LogTimes   Output: list of UTCs
    timesUTC=[]
    for i in range(0,len(times)):
        string=times[i]
        year=int(string[0:4])
        month=int(string[5:7])
        day=int(string[8:10])
        hour=int(string[11:13])
        minute=int(string[14:16])
        second=int(string[17:19])
        timesUTC.append(UTCDateTime(year,month,day,hour,minute,second))
    return timesUTC

def UTC2LogTime(times): #Input: list of UTCs     Output: list of logtimes
    print("working!")
    LogTimes=[]
    for i in range(0,len(times)):
        UTC=times[i]
        year=str(UTC.year)
        month=str(UTC.month)
        day=str(UTC.day)
        hour=str(UTC.hour)
        minute=str(UTC.minute)
        second=str(UTC.second)
        if len(month)==1:
            month='0'+month
        if len(day)==1:
            day='0'+day
        if len(hour)==1:
            hour='0'+hour
        if len(minute)==1:
            minute='0'+minute
        if len(second)==1:
            second='0'+second
        LogTimes.append(year+'-'+month+'-'+day+'T'+hour+':'+minute+':'+second)
        print(LogTimes[i])
    return LogTimes

#################################
#I/O
#################################


def WriteTriggers(list,filename): #Input: list of log times, filename  #output: written file
    lines=''
    for i in range(0,len(list)):
        lines=lines+list[i]+'\n'
    ref=open(filename,'a')
    ref.writelines(lines)
    ref.close()

def ReadTriggers(filename): #Input: file name of trigger times; Output: [UTC trigger times]
    ref=open(filename,'r')
    triggertimes=ref.readlines()
    triggersUTC=LogTime2UTC(triggertimes) #Change this to noise for noise
    ref.close()
    return triggersUTC

###################################
#READING AND WRITING TO A TEXT FILE
###################################

def ReadLine(filename,skipped): #opens "filename," skips lines, and returns the next line as an output list
    ref=open(filename,"r")
    for i in range(0,skipped):
        ref.readline()
    return ref.readline()
    ref.close()

#Reads a file, skipps lines and entries, and then reads #entriesread
def ReadEntries(filename,linesskipped,entriesskipped,entriesread): #opens "filename", skips lines and entries, and reads #entriesread
    ref=open(filename,"r")
    for i in range(0,linesskipped):
        ref.readline()
    entries=ref.read().split()
    entries.reverse() 
    for i in range(0,entriesskipped):
        entries.pop()
    entries.reverse()
    for i in range(0,len(entries)-entriesread):
        entries.pop()        
    return entries
    ref.close()

###################################
#CATALOG CATALOG CATALOG CATALOG
###################################
def FindArrivalTimes(cat,latstation,lonstation): #Input: catalog, lat/long of station; Output: [arrival times]
    #Assemble list of origins: locations[i], depths[i], and picktimes[i])
    locations=[]
    depths=[]
    picktimes=[]
    for i in range(0,len(cat)):
        latquake=cat[i].origins[0].latitude
        lonquake=cat[i].origins[0].longitude
        locations.append((latquake,lonquake))
        depths.append(cat[i].origins[0].depth/1000)
        picktimes.append(cat[i].origins[0].time)
    #Compile list of arrival times
    arrivaltimes=[]
    resultstotal=[]
    for i in range(0,len(cat)):
        results=ne.Client().getTravelTimes(latitude=latstation,longitude=lonstation,depth=depths[i],locations=[locations[i]],model='iasp91') #Get dictionary of travel times
        resultstotal.append(results)
        delaytime=results[0].copy().items()[0][1]/1000 #/1000 converts from s to ms
        arrivaltimes.append(picktimes[i]+delaytime)
    #    for j in range(0,len(results[0])):
    #        delaytime=results[0].copy().items()[j][1]/1000 #/1000 converts from s to ms
    #        arrivaltimes.append(picktimes[i]+delaytime)
            
    return resultstotal,arrivaltimes
    
def CatFilter(startUTC,endUTC,lat,lon,minrad,maxrad,minmag,maxmag):
    cat = Client().get_events(starttime=startUTC, endtime=endUTC,latitude=lat,longitude=lon,minradius=minrad,maxradius=maxrad,minmagnitude=minmag,maxmagnitude=maxmag)
    #cat.filter('latitude<=0')
    #cat=cat.filter('longitude <= 0')
    return cat
