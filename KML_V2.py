
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
import glob
import os
from datetime import datetime, timedelta
from ADSB_Internet_Info import get_registration




#log_file_folder = 'E:\workspace\ADSB\log_archive\\from_Pi\March_2015\*.log'
log_file_folder = 'E:\workspace\ADSB\*.log'

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
    

def array_to_list(lat, lon,alt):
    out = ''
    for line in zip(lat,lon,alt):
        s = str(line[1]) + "," + str(line[0]) + "," + str(line[2]) + '\n'
        out = out + s
    return out

def kml_header():
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
                                               KML.color('ffff00ff'),
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
    return doc

def write_legs(legs, ident):
    fld = KML.Folder(
                     KML.name(ident)
                    )
    for leg in legs:
        fld.append(write_leg(leg, ident))
    fld.append(last_leg(legs[-1], ident))
    return fld

def last_leg(leg, registration):
    time = []
    lat = []
    lon = []
    alt = []
    for point in leg:
        time.append(point[0])
        lat.append(point[1])
        lon.append(point[2])
        alt.append(str(float(point[3])*0.3048))
    
            
    linestyle = "#ActiveTrack"
    airplanestyle = "#ActiveAirplane"
    visibility = '1'
    #print lat
    doc = KML.Placemark(KML.name(registration),
                        KML.visibility(visibility),
                        KML.styleUrl(airplanestyle),
                        KML.Point(KML.coordinates(str(lon[-1]) + "," + str(lat[-1]) + "," +  str(alt[-1])
                                                  ),
                                  KML.altitudeMode('absolute')
                                  ),
                        
                        )
    doc.append(KML.Placemark(
                             KML.name(time[0]),
                             KML.visibility(visibility),
                             KML.styleUrl(linestyle),
                             KML.LineString(
                                            KML.extrude(0),
                                            GX.altitudeMode("absolute"),
                                            KML.coordinates(
                                                            array_to_list(lat, lon, alt)
                                                            )
                                            )
                             )
               )
    return doc
    

def write_leg(leg, ident):
    #print ident
    #print leg
    time = []
    lat = []
    lon = []
    alt = []
    for point in leg:
        time.append(point[0])
        lat.append(point[1])
        lon.append(point[2])
        alt.append(str(float(point[3])*0.3048))
        
    linestyle = "#InactiveTrack"
    airplanestyle = "#InactiveAirplane"
    visibility = '1'
    #print lat

    
    
    #print registration
    doc = KML.Placemark(
                  KML.name(time[0]),
                  KML.visibility(visibility),
                  KML.styleUrl(linestyle),
                  KML.LineString(
                                 KML.extrude(0),
                                 GX.altitudeMode("absolute"),
                                 KML.coordinates(
                                                 array_to_list(lat, lon, alt)
                                                 )
                                 )
                  )
    
    #print etree.tostring(doc, pretty_print=True)
    #out_kml = open("first.kml", 'w')
    #out_kml.write(etree.tostring(doc, pretty_print=True))
    #out_kml.close()
    
    return doc

def text_to_datetime(time):
    time = time.strip('\0')
    try:
        last_seen = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
    except:
        last_seen = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return last_seen

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)

def add_internet_info_to_file(ident,file):
    
    line = "*Reg:" + ident + '\n' 
    #print line
    fo = open(file, 'a')
    fo.write(line)
    fo.close()

def scan_logs():
    #print "Updating KML"
    files = glob.glob(log_file_folder) #scan whole folder
    #files = ['E:\\workspace\\ADSB\\log_archive\\from_Pi\\March_2015\\49D006.log']
    kml_file = kml_header()
    #print files
    active_aircraft = False
    for fname in files:
        date = modification_date(fname)
        #print date
        if check_if_active(date):
            #print fname
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
                #print line
                if line.startswith('*'):
                    #print line
                    if line.startswith('*Reg:'):
                        ident = line.lstrip('*Reg:')
                        check_internet_for_ident = False
                else:
                    line = line.strip('\0')
                    words = line.rstrip().split(';')
                    #print words
                    if len(words) == 4:
                        time.append(words[0])
                        lat.append(words[1])
                        lon.append(words[2])
                        alt.append(str(float(words[3])*0.3048))
            #if check_if_active(time[-1]):
            #    doc.append(write_kml(time, lat, lon, alt, ident)).
            #print ident
            #get the registration of the aircraft if we haven't done it before. 
            if False: #check_internet_for_ident:
                reg = get_registration(ident)
                if reg is not ident:
                    add_internet_info_to_file(reg,fname)
                    print "Adding to file"
                    ident = reg
            
            
            #scroll through the position points and break it up where the time delta
            #is big enough that it's a separate sighting 
            legs = []
            leg = [(time[0], lat[0], lon[0], alt[0])]
            #print leg[-1][0]
            for point in zip(time[1:], lat[1:], lon[1:], alt[1:]):
                last_seen = text_to_datetime(leg[-1][0])
                #print file
                this_seen = text_to_datetime(point[0])
                delay = this_seen - last_seen
                if delay > timedelta(minutes = 30):
                    legs.append(leg)
                    leg = []
                    leg.append(point)
                    
                else:
                    leg.append(point)
            legs.append(leg)
                    
            #print legs[1:5]
                
            kml_file.append(write_legs(legs, ident))
                
                
    #print etree.tostring(kml_file, pretty_print=True)          
        
    out_kml = open("KML_V2.kml", 'w')
    #out_kml = open("moonshadow.kml", 'w')
    out_kml.write(etree.tostring(kml_file, pretty_print=True))
    out_kml.close()






if __name__ == '__main__':
    #do this stuff when run standalone
    scan_logs()   