from obspy import UTCDateTime
from obspy.fdsn import Client
from petfun import*

startUTC=UTCDateTime("2014-01-5T00:00:00")
windowtime=24*60**2
delaytime=0

endUTC=startUTC+windowtime
startUTC-=delaytime

'''
fdsn_client = Client(base_url="http://service.geonet.org.nz") 
earthquakes = fdsn_client.get_waveforms("NZ","WIZ","10","HHZ",startUTC,endUTC,attach_response=True)
earthquakes.detrend('constant')

pre_filt = (0.05, 0.06, 30.0, 35.0)
earthquakes.remove_response(output='DISP', pre_filt=pre_filt)
earthquakes.plot()
'''
st=GetStreamJava('WIZ','Z',startUTC,windowtime)

st.plot(type='dayplot')

#AllPlotsList([startUTC],windowtime,0)

#earthquakes[0].spectrogram()


