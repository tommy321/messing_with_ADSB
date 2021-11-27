
#!/usr/bin/python
'''Example of using pyKML to visualize ephemeris data

This example demonstrates how pyKML can be used visualize geospatial data 
generated by another Python library, PyEphem (http://rhodesmill.org/pyephem/).

Example usage:
python pyephem_example.py > test.kml
'''

from datetime import datetime, timedelta
from math import pi, degrees, radians
from operator import mod
import ephem
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
import glob
import os
from ADSB_Internet_Info import get_registration
import moon
from KML_V2 import add_internet_info_to_file



log_file_folder = 'E:\workspace\ADSB\*.log'

def array_to_list(lat, lon,alt):
    out = ''
    for line in zip(lat,lon,alt):
        s = str(line[1]) + "," + str(line[0]) + "," + str(line[2]) + '\n'
        out = out + s
    return out

def text_to_datetime(time):
    try:
        last_seen = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
    except:
        last_seen = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return last_seen

def future_path(lat, lon, alt, time):
    future_lat = []
    future_lon = []
    future_alt = []
    if len(lat)>2:
        delta_lat = float(lat[-1]) - float(lat[-2])
        delta_lon = float(lon[-1]) - float(lon[-2])
        delta_alt = float(alt[-1]) - float(alt[-2])
        
        delta_time = text_to_datetime(time[-1]) - text_to_datetime(time[-2])
        
        #print delta_lat, delta_lon, delta_alt, delta_time
        timeout = timedelta(seconds = 30)
        if delta_time < timeout: #we should predict the track
            
            future_lat.append(float(lat[-1]))
            future_lon.append(float(lon[-1]))
            future_alt.append(float(alt[-1]))
            
            
            predict_time = 180.0 #predict 300 seconds or 5 minutes into the future
            delta_time_seconds = delta_time.seconds + delta_time.microseconds/1000000.0
            try:
                scale_factor = predict_time/delta_time_seconds
            except:
                return [],[],[] 
                
            #print "Delta Time: ", delta_time, " Predict_Time: ", predict_time, " Scale_Factor: ", scale_factor
            future_lat.append(float(lat[-1])+delta_lat*scale_factor)
            future_lon.append(float(lon[-1])+delta_lon*scale_factor)
            future_alt.append(float(alt[-1])+delta_alt*scale_factor)
            #print " Next Lat: ", future_lat, " Next Lon: ", future_lon, "Next Alt: ", future_alt
    return future_lat, future_lon, future_alt

def write_kml(time, lat, lon, alt, ident):
    airplane_is_active = check_if_active(time[-1])
    if airplane_is_active:
        linestyle = "#ActiveTrack"
        airplanestyle = "#ActiveAirplane"
        shadowstyle = '#ActiveShadow'
        futurepath = '#FuturePath'
        futureshadowpath = '#FutureShadowPath'
        visibility = '1'
    else:
        linestyle = "#InactiveTrack"
        airplanestyle = "#InactiveAirplane"
        shadowstyle = '#InactiveShadow'
        futurepath = '#FuturePath'
        futureshadowpath = '#FutureShadowPath'
        visibility = '0' #change this back to zero to erase inactive tracks.
        
    #registration = ADSB_Internet_Info.get_registration(ident)
    registration = ident
    
    #get moon shadow location:
    #print len(lat)
    #print "From KML: ", lat, lon, alt, time
    shadow_lat, shadow_lon, shadow_time = moon.get_moon_shadow_V3(lat, lon, alt, time)
    shadow_lat_V1, shadow_lon_V1, shadow_time_V1 = moon.get_moon_shadow(lat, lon, alt, time)
    if airplane_is_active:
        future_lat, future_lon, future_alt = future_path(lat, lon, alt, time)
        future_shadow_lat, future_shadow_lon, future_shadow_alt = future_path(shadow_lat, shadow_lon, [0.0, 0.0], time)
    else:
        future_lat, future_lon, future_alt = [], [], []
        future_shadow_lat, future_shadow_lon, future_shadow_alt = [], [], []
    #if future_shadow_lat:
    #    print "future Lat: ", future_shadow_lat
    #    print "future Lon: ", future_shadow_lon
    #    print "future alt: ", future_shadow_alt
        
    #print "Shadow Lat: ", shadow_lat
    #print "Shadow Lon: ", shadow_lon
    #print "Shadow time: ", shadow_time
    
    
    
    #print registration
    doc = KML.Folder(
                     KML.name(registration),
                     KML.Placemark(
                                   KML.name(registration),
                                   KML.visibility(visibility),
                                   KML.styleUrl(linestyle),
                                   KML.LineString(
                                                  KML.extrude(0),
                                                  GX.altitudeMode("absolute"),
                                                  KML.coordinates(
                                                                  array_to_list(lat, lon, alt)
                                                                  )
                                                  )
                                   ),
                     KML.Placemark(
                                   KML.name("Moon Shadow"),
                                   KML.visibility(visibility),
                                   KML.styleUrl(shadowstyle),
                                   KML.LineString(
                                                  KML.extrude(0),
                                                  GX.altitudeMode("clampToGround"),
                                                  KML.coordinates(
                                                                  array_to_list(shadow_lat, shadow_lon, shadow_lon)
                                                                  )
                                                  )
                                   ),
                     KML.Placemark(
                                   KML.name("Future Path"),
                                   KML.visibility(visibility),
                                   KML.styleUrl(futurepath),
                                   KML.LineString(
                                                  KML.extrude(0),
                                                  GX.altitudeMode("absolute"),
                                                  KML.coordinates(
                                                                  array_to_list(future_lat, future_lon, future_alt)
                                                                  )
                                                  )
                                   ),
                     KML.Placemark(
                                   KML.name("V1 Shadow"),
                                   KML.visibility(visibility),
                                   KML.styleUrl('V1Shadow'),
                                   KML.LineString(
                                                  KML.extrude(0),
                                                  GX.altitudeMode("clampToGround"),
                                                  KML.coordinates(
                                                                  array_to_list(shadow_lat_V1, shadow_lon_V1, shadow_lon_V1)
                                                                  )
                                                  )
                                   ),
                     KML.Placemark(
                                   KML.name("Future Shadow"),
                                   KML.visibility(visibility),
                                   KML.styleUrl(futureshadowpath),
                                   KML.LineString(
                                                  KML.extrude(0),
                                                  GX.altitudeMode("clampToGround"),
                                                  KML.coordinates(
                                                                  array_to_list(future_shadow_lat, future_shadow_lon, future_shadow_alt)
                                                                  )
                                                  )
                                   ),
                     KML.Placemark(
                                   KML.name(registration),
                                   KML.visibility(visibility),
                                   KML.styleUrl(airplanestyle),
                                   KML.Point(KML.coordinates(
                                                             str(lon[-1]) + "," + str(lat[-1]) + "," +  str(alt[-1])
                                                             ),
                                             KML.altitudeMode('absolute')
                                             )
                                   )
                     )
    #print etree.tostring(doc, pretty_print=True)
    #out_kml = open("first.kml", 'w')
    #out_kml.write(etree.tostring(doc, pretty_print=True))
    #out_kml.close()
    return doc

def scan_logs():
    print "Updating KML"
    doc = KML.Document(
                       KML.open('1'),
                       KML.name("ADSB"), 
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
                                               KML.color('5500ffff'),
                                               KML.width('2'),
                                               ),
                                 KML.styleUrl('#V1Shadow'),
                                 id="V1Shadow"
                                 ),
                       KML.Style(
                                 KML.LineStyle(
                                               KML.color('ff000000'),
                                               KML.width('2'),
                                               ),
                                 KML.styleUrl('#InactiveShadow'),
                                 id="InactiveShadow"
                                 ),
                       KML.Style(
                                 KML.LineStyle(
                                               KML.color('ffff0000'),
                                               KML.width('2'),
                                               ),
                                 KML.styleUrl('#FuturePath'),
                                 id="FuturePath"
                                 ),
                       KML.Style(
                                 KML.LineStyle(
                                               KML.color('ffffff00'),
                                               KML.width('2'),
                                               ),
                                 KML.styleUrl('#FutureShadowPath'),
                                 id="FutureShadowPath"
                                 )
                       )
    
    files = glob.glob(log_file_folder)
    #print files
    active_aircraft = False
    for fname in files:
        date = modification_date(fname)
        #print fname
        if check_if_active(date):
            active_aircraft = True
            check_internet_for_ident = True
            #print fname
            file = open(fname, 'r')
            ident = os.path.split(fname)[1].split('.')[0]
            #print ident
            time = []
            lat = []
            lon = []
            alt = [] 
            for line in file:
                if line.startswith('*'):
                    #print line
                    if line.startswith('*Reg:'):
                        #ident = line.lstrip('*Reg:') #uncomment this line if you want the canadian registration displayed. 
                        #print line
                        check_internet_for_ident = False
                else:
                    words = line.rstrip().split(';')
                    time.append(words[0])
                    lat.append(words[1])
                    lon.append(words[2])
                    alt.append(str(float(words[3])*0.3048))
            if check_if_active(time[-1]):
                doc.append(write_kml(time, lat, lon, alt, ident))
            if check_internet_for_ident:
                reg = get_registration(ident)
                #print "Getting Internet Data for:" + ident + " " + reg
                if reg is not ident:
                    add_internet_info_to_file(reg,fname)
                    #print "Adding to file"
                    ident = reg
    
    #print lat
    #print lon
    #print alt
    #print ident
    
    #array_to_list(lat, lon, alt)
    
    if active_aircraft == True:
        
        #print etree.tostring(doc, pretty_print=True)
        out_kml = open("first.kml", 'w')
        #out_kml = open("moonshadow.kml", 'w')
        out_kml.write(etree.tostring(doc, pretty_print=True))
        out_kml.close()
    
def check_if_active(time, timeout = timedelta(seconds = 180)):
    #print time
    if isinstance(time, datetime):
        last_seen = time
    else:
        last_seen = text_to_datetime(time)
    timenow = datetime.now()
    since_seen = timenow - last_seen
    if since_seen > timeout:
        return False
    else:
        return True
    
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)
    
    
if __name__ == '__main__':
    #do this stuff when run standalone
    scan_logs()      
    #files = glob.glob(log_file_folder)
    #for fname in files:
    #    file = open(fname, 'r')
    #    ident = os.path.split(fname)[1].split('.')[0]
    #    #print ident
    #    time = []
    #    lat = []
    #    lon = []
    #    alt = [] 
    #    for line in file:
    #        words = line.rstrip().split(';')
    ##        time.append(words[0])
    #        lat.append(words[1])
    #        lon.append(words[2])
    #        alt.append(str(float(words[3])*0.3048))
    #    print time[-1]
    #    last_seen = datetime.strptime(time[-1], '%Y-%m-%d %H:%M:%S.%f')
    ##    timenow = datetime.now()
    # #   since_seen = timenow - last_seen
    #    print check_if_active(last_seen)

