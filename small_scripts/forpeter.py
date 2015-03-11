from obspy import UTCDateTime
from obspy.fdsn import Client

startUTC=UTCDateTime("2011-07-06T19:03:20")
windowtime=600
delaytime=30

endUTC=startUTC+windowtime
startUTC-=delaytime
fdsn_client = Client(base_url="http://service.geonet.org.nz") 

earthquakes = fdsn_client.get_waveforms("NZ","WIZ","10","HHZ",startUTC,endUTC,attach_response=True)

earthquakes.detrend('constant')

#print earthquakes[0].stats

pre_filt = (0.05, 0.06, 40.0, 45.0)
earthquakes.remove_response(output='DISP', pre_filt=pre_filt)
earthquakes.plot()

#earthquakes[0].spectrogram()


