from datetime import datetime, timedelta
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX

def kml_head():
    doc = KML.Document(
                       KML.open('1'),
                       KML.name("ADSB Timelines"), 
                       KML.Style(
                                 KML.visibility("0"),
                                 KML.color('55ffffff'),
                                               KML.LabelStyle(
                                                              KML.color('55ffffff'),
                                                              KML.scale('0.6'),
                                                              ),
                                 KML.IconStyle(
                                               KML.color('55ffffff'),
                                               KML.Icon(KML.href('http://maps.google.com/mapfiles/kml/shapes/airports.png'),
                                                        ),
                                               
                                               ),
                                 
                                 KML.styleUrl('#InactiveAirplane'),
                                 id="InactiveAirplane"
                                 ),
                       KML.Style(
                                 KML.IconStyle(
                                               KML.color('ffffffff'),
                                               KML.Icon(
                                                        KML.href('http://maps.google.com/mapfiles/kml/shapes/airports.png'),
                                                        ),
                                               ),
                                 KML.styleUrl('#ActiveAirplane'),
                                 id="ActiveAirplane"
                                 ),
                       KML.Style(
                                 KML.LineStyle(
                                               KML.color('44ffffff'),
                                               KML.width('1'),
                                               KML.visibility("0"),
                                               ),
                                 KML.styleUrl('#InactiveTrack'),
                                 id="InactiveTrack"
                                 ),
                       KML.Style(
                                 KML.LineStyle(
                                               KML.color('ff0000ff'),
                                               KML.width('2'),
                                               ),
                                 KML.styleUrl('#ActiveTrack'),
                                 id="ActiveTrack"
                                 ),
                       KML.Style(
                                 KML.LineStyle(
                                               KML.color('ff00ff00'),
                                               KML.width('2'),
                                               ),
                                 KML.styleUrl('#ActiveShadow'),
                                 id="ActiveShadow"
                                 ),
                       KML.Style(
                                 KML.LineStyle(
                                               KML.color('ff000000'),
                                               KML.width('2'),
                                               ),
                                 KML.styleUrl('#InactiveShadow'),
                                 id="InactiveShadow"
                                 )
                       )
    return doc

def string_to_datetime(string):
    try:
        last_seen = datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')
    except:
        last_seen = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
    return last_seen
                                      


test_log_file = 'E:\workspace\ADSB\C021F6.log'

file = open(test_log_file, 'r')
time = []
lat = []
lon = []
alt = [] 
for line in file:
    words = line.rstrip().split(';')
    time.append(string_to_datetime(words[0]))
    lat.append(words[1])
    lon.append(words[2])
    alt.append(str(float(words[3])*0.3048))

timeout = timedelta(minutes = 30) #timeout to consider the next data point a new observation of the same airplane
flights = []
flight = []
last_time = time[0]
for data in zip(time, lat, lon, alt):
    if data[0]-last_time<timeout:
        flight.append(data)
    else:
        flights.append(flight)
        flight = []
    last_time = data[0]

doc = kml_head()
foldername = test_log_file.split('\\')[-1]
foldername = foldername.split('.')[0]
#print foldername
doc.append(KML.Folder(
                 KML.name(foldername)
                 )
           )

                 
for flight in flights:
    placemark name = flight[0][0].strftime('%Y-%m-%d %H:%M')
    




#print etree.tostring(doc, pretty_print=True)
out_kml = open("timeline.kml", 'w')
#out_kml = open("moonshadow.kml", 'w')
out_kml.write(etree.tostring(doc, pretty_print=True))
out_kml.close()




    
    
