from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
import glob
import os
from datetime import datetime, timedelta
from ADSB_Internet_Info import get_registration


def array_to_list(lat, lon,alt):
    out = ''
    for line in zip(lat,lon,alt):
        s = str(line[1]) + "," + str(line[0]) + "," + str(line[2]) + '\n'
        out = out + s
    return out

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)
def text_to_datetime(time):
    time = time.strip('\0')
    try:
        last_seen = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
    except:
        last_seen = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return last_seen

def write_legs(legs, ident):
    fld = KML.Folder(
                     KML.name(ident)
                    )
    for i, leg in enumerate(legs):
        leg_id = ident + "_" + str(i)
        fld.append(write_leg(leg, ident, leg_id))
    if len(legs)>0:
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
                        id=registration)
    return doc
    

def write_leg(leg, ident, leg_id = ""):
    #print ident
    print leg_id
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
                                 ),
                        id=leg_id
                        )
    
    #print etree.tostring(doc, pretty_print=True)
    #out_kml = open("first.kml", 'w')
    #out_kml.write(etree.tostring(doc, pretty_print=True))
    #out_kml.close()
    
    return doc


def kml_header(trail_length = 10):
    fade_legs = []
    fade_colours = []
    fade_step = int(255/trail_length)
    print fade_step
    for i in range(trail_length+1):
        fade_legs.append("#leg_" + str(i))
        fade_colours.append(str(hex(fade_step * i)).strip('0x') + "0000ff")
    fade_colours[0] = "000000ff"
    fade_colours[-1] = "ff0000ff"
    print fade_legs
    print fade_colours
        
    doc = KML.Document(
                       KML.open('1'),
                       KML.name("ADSB Playback"), 
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
    
    for leg_id, colour in zip(fade_legs, fade_colours):
        #print leg_id, colour
        doc.append(KML.Style(
                                 KML.LineStyle(
                                               KML.color(colour),
                                               KML.width('2'),
                                               ),
                                 KML.styleUrl(leg_id),
                                 id=leg_id
                                 )
                   )
    #print etree.tostring(doc, pretty_print=True)    
    return doc


def animate_leg(lat, lon, alt, time, ident):
    fld = KML.Folder(
                     KML.name("Path")
                    )
    
    
    print etree.tostring(fld, pretty_print=True) 
    return fld


def scan_logs(trail_length = 10):
    print "Updating KML"
    #files = glob.glob(log_file_folder) #scan whole folder
    files = ['E:\\workspace\\ADSB\\log_archive\\from_Pi\\March_2015\\49D006.log']
    kml_file = kml_header(trail_length)
    #print files
    active_aircraft = False
    for fname in files:
        date = modification_date(fname)
        #print date
        if True: #check_if_active(date):
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
            if check_internet_for_ident:
                reg = get_registration(ident)
                if reg is not ident:
                    add_internet_info_to_file(reg,fname)
                    print "Adding to file"
                    ident = reg
            print len(time)
    kml_file.append(animate_leg(lat, lon, alt, time, ident))
            
            
    print etree.tostring(kml_file, pretty_print=True)
    out_kml = open("ADSB_Tour.kml", 'w')
    out_kml = open("ADSB_Tour.kml", 'w')
    out_kml.write(etree.tostring(kml_file, pretty_print=True))
    out_kml.close()
    
            
            
            

if __name__ == '__main__':
    #do this stuff when run standalone
    
    trail_length = 10
    scan_logs(trail_length)               