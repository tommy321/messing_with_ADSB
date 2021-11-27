
from datetime import datetime, timedelta
from math import pi, degrees, radians, asin, acos, tan, sin, cos, sqrt, atan2
from operator import mod
import ephem
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

year = 2014
month = 10
day = 30
longitude = -75.917117 # [degrees]
latitude =  45.355226  # [degrees]
elevation = 70     # elevation above sea level [meters]
height = 2            # height of observer [meters]
timezone_offset = -4   # time offset from UTC time [hours]
label_distance = 100  # distance along ephemeris vector [meters]



def adjust_heading_degrees(alpha):
    '''add the heading angle to make it between -180 and 180 degrees'''
    return mod(alpha+180,360)-180

def normalize_vector(x,y,z):
    '''return a unit normal vector'''
    length = (x**2+y**2+z**2)**0.5
    return x/length, y/length, z/length

def calculate_geographic_offset(azimuth_angle,altitude_angle, distance):
    '''determine the displacement in terms of latitude, longitude, and altitude'''
    from math import sin, cos, tan, atan2

    R = 6371009  # radius of earth in meters
    dx,dy,dz = normalize_vector(
        sin(azimuth_angle),
        cos(azimuth_angle),
        tan(altitude_angle),
    )
    alpha = atan2(dy,dx)   # horizontal angle [radians]
    D_horiz = distance*(dx**2+dy**2)**0.5  # horizontal length [meters]
    delta_lat_rad = D_horiz*sin(alpha)/R  # latitude offset [radians]
    delta_lon_rad = D_horiz*cos(alpha)/(R*cos(radians(latitude))) # longitude offset [radians]
    delta_alt = distance*dz  # altitude offset [meters]
    return delta_lat_rad, delta_lon_rad, delta_alt




def dummy_function():
    obs = ephem.Observer()
    obs.long, obs.lat = str(longitude), str(latitude) 
    obs.elev = elevation + height
    moon = ephem.Moon()
    data = {}
    date = datetime.utcnow()
    obs.date = '{year}/{month}/{day} {hour}:{minute}'.format(
        year = date.year,
        month = date.month,
        day = date.day,
        hour = date.hour,
        minute = date.minute,
        )
    moon.compute(obs)
    
    print moon
    data['datetime UTC'] =  date
    data['azimuth_angle'] = moon.az.real
    data['altitude_angle'] = moon.alt.real
    print type(date.strftime('%H:%M'))
    print type(date)
    print datetime.utcnow()
    print data
    
    
    timestamp = data['datetime UTC']
    azimuth_rad = data['azimuth_angle']
    azimuth_deg = degrees(azimuth_rad)
    altitude_rad = data['altitude_angle']
    altitude_deg = degrees(altitude_rad)
    
def kml_skeleton():
    # create a KML file skeleton
    stylename = "sn_shaded_dot"
    doc = KML.kml(
        KML.Document(
            KML.Name("Moon Position"),
            KML.Style(
                KML.IconStyle(
                    KML.scale(1.2),
                    KML.Icon(
                        KML.href("http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png")
                    ),
                ),
                id=stylename,
            )
        )
    )
    return doc
    
    
    
def check_moon_shadow():    
    # create placemark for the observer, and add it to the KML document
    latitude = '45.355226' 
    longitue = '-75.917117'
    pm_observer = KML.Placemark(
        KML.name('Aircraft'),
        KML.Camera(
                   KML.longitude(longitude),
                   KML.latitude(latitude),
                   KML.altitude(2),
                   KML.heading(azimuth_deg),
                   KML.tilt(90+altitude_deg),
                   KML.altitudeMode('relativeToGround')),
        KML.styleUrl('#{0}'.format(stylename)),
        KML.Point(
            KML.extrude(True),
            KML.altitudeMode('relativeToGround'),
            KML.coordinates("{0},{1},{2}".format(longitude,latitude,height)),
        ),
    )
    
    doc.Document.append(pm_observer)
    if altitude_deg > 0:
            # define a placemark along the ephemeris vector for labeling
            delta_lat_rad, delta_lon_rad, delta_alt = calculate_geographic_offset(
                azimuth_angle=radians(adjust_heading_degrees(degrees(azimuth_rad))),
                altitude_angle=altitude_rad,
                distance=label_distance,
            )
            pm1 = KML.Placemark(
                KML.name((timestamp.strftime('%H:%M')),
                KML.LookAt(
                    KML.longitude(longitude),
                    KML.latitude(latitude),
                    KML.altitude(height),
                    KML.heading(adjust_heading_degrees(azimuth_deg)),
                    KML.tilt(90),
                    KML.roll(0),
                    KML.altitudeMode("relativeToGround"),
                    KML.range(50),
                ),
                KML.Point(
                    KML.styleUrl('#{0}'.format(stylename)),      
                    KML.altitudeMode("relativeToGround"),
                    KML.coordinates("{lon},{lat},{alt}".format(
                        lon = longitude + degrees(delta_lon_rad),
                        lat = latitude + degrees(delta_lat_rad),
                        alt = height + delta_alt,
                    )),
                ),
            )
                                )
            pm2 = KML.Placemark(
                KML.name('Moon View'),
                KML.LookAt(
                    KML.longitude(longitude),
                    KML.latitude(latitude),
                    KML.altitude(height),
                    KML.heading(adjust_heading_degrees(180+azimuth_deg)),
                    KML.tilt(90-altitude_deg-0.2),
                    KML.roll(0),
                    KML.altitudeMode("relativeToGround"),
                    KML.range(2*label_distance),
                ),
                KML.Model(
                    KML.altitudeMode('relativeToGround'),
                    KML.Location(
                        KML.longitude(longitude),
                        KML.latitude(latitude),
                        KML.altitude(height),
                    ),
                    KML.Orientation(
                        KML.heading(adjust_heading_degrees(azimuth_deg)),
                        KML.tilt(90-altitude_deg),
                        KML.roll(0),
                    ),
                    KML.Scale(
                        KML.x(1000),
                        KML.y(1000),
                        KML.z(500000),
                    ),
                    KML.Link(
                        KML.href('unit_cone_red.dae'),
                    ),
                ),
            )
            doc.Document.append(
                KML.Folder(
                    KML.name(timestamp.strftime('%H:%M')),
                    pm1,
                    pm2,
                    KML.TimeStamp(
                        KML.when(timestamp.strftime('%Y-%m-%dT%H:%MZ')),
                    ),
                )
            )
    
    print etree.tostring(doc, pretty_print=True)
    out_kml = open("moon.kml", 'w')
    out_kml.write(etree.tostring(doc, pretty_print=True))
    out_kml.close()

def get_moon_shadow(in_lat, in_long, in_alt, in_time):
    
    time_zone_delta = 4
    tz = timedelta(hours = time_zone_delta)
    shadow_lat = []
    shadow_lon = []
    shadow_time = []
    #print "Input Size: ", len(in_lat)
    for lat, lon, alt, time in zip(in_lat, in_long, in_alt, in_time):
        #print "Time: ",type(time)
        #print "Lat: ", type(lat)
        #print "Long: ",type(lon)
        #print "Alt: ", type(alt)
        if isinstance(lat, str):
            lat = float(lat)
            lon = float(lon)
            alt = float(alt)
        
        if isinstance(time, datetime):
            time = time + tz
        else:
            try:
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f') + tz
            except:
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S') + tz
        #print "Time: ", time
        obs = ephem.Observer()
        obs.long, obs.lat = str(lon), str(lat)
        alt_meters = float(alt)*0.3048 - 90.0
        obs.elev = alt_meters
        moon = ephem.Moon()
        data = {}
        date = time
        obs.date = '{year}/{month}/{day} {hour}:{minute}'.format(
            year = date.year,
            month = date.month,
            day = date.day,
            hour = date.hour,
            minute = date.minute,
            )
        moon.compute(obs)
        #print moon
        azimuth_rad = moon.az.real
        altitude_rad = moon.alt.real
        #print "Aircraft Lat: ", lat
        #print "Aircraft Lon: ", lon
        #print "Aircraft Alt: ", alt
        #print "Azimuth Rad: ", degrees(azimuth_rad)
        #print "Altitude_Rad: ", altitude_rad
        #print data
        if altitude_rad > 0.01:
            #reverse the azimuth value
            rev_az = azimuth_rad + pi
            rev_az = mod(rev_az, 2.0*pi)
            #reverse the elevation value
            rev_el = pi/2.0-altitude_rad
            
            #print "Shadow Az: ", degrees(rev_az), "Shadow El: ", degrees(rev_el)
            R = 6371009  # radius of earth in meters
            #print "Alt_Meters: ", alt_meters
            #print "rev_el: ", rev_el
            #print "rev_az: ", rev_az
            
            delta_lat = asin(alt_meters*tan(rev_el)*cos(rev_az)/2.0/R)
            delta_lon = asin(alt_meters*tan(rev_el)*sin(rev_az)/2.0/R)
            #print "Delta Lon: ", delta_lon, "Lon:", lon
            delta_lon = delta_lon*cos(radians(lat))
            #print "Corrected Delta Lon: ", delta_lon, "Lon:", lon
            shadow_lat.append(lat+degrees(delta_lat))
            shadow_lon.append(lon+degrees(delta_lon))
            shadow_time.append(time)
            #print "Shadow lat: ", shadow_lat, "Shadow long: ", shadow_lon
    return shadow_lat, shadow_lon, shadow_time
        
                
        
def get_moon_shadow_V2(in_lat, in_long, in_alt, in_time):
    #calculate the moons iteratively.
    time_zone_delta = 4
    tz = timedelta(hours = time_zone_delta)
    shadow_lat = []
    shadow_lon = []
    shadow_time = []
    #print "Input Size: ", len(in_lat)
    for lat, lon, alt, time in zip(in_lat, in_long, in_alt, in_time):
        #print "Time: ",type(time)
        #print "Lat: ", type(lat)
        #print "Long: ",type(lon)
        #print "Alt: ", type(alt)
        if isinstance(lat, str):
            lat = float(lat)
            lon = float(lon)
            alt = float(alt)
        
        if isinstance(time, datetime):
            time = time + tz
        else:
            try:
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f') + tz
            except:
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S') + tz
        #print "Time: ", time
        obs = ephem.Observer()
        obs.long, obs.lat = str(lon), str(lat)
        alt_meters = float(alt)*0.3048 - 90.0
        obs.elev = alt_meters
        moon = ephem.Moon()
        data = {}
        date = time
        obs.date = '{year}/{month}/{day} {hour}:{minute}'.format(
            year = date.year,
            month = date.month,
            day = date.day,
            hour = date.hour,
            minute = date.minute,
            )
        moon.compute(obs)
        print moon
        azimuth_rad = pi/4#moon.az.real
        altitude_rad = pi/4 #moon.alt.real
        print "Aircraft Lat: ", lat
        print "Aircraft Lon: ", lon
        print "Aircraft Alt: ", alt
        print "Azimuth Rad: ", degrees(azimuth_rad)
        print "Altitude_Rad: ", degrees(altitude_rad)
        
        #aircraft height above earth center.
        RE = radius_wgs84(radians(lat))
        RS = RE #spherical earth
        ThetaRS = pi/2.0 - altitude_rad #shadow angle at aircraft
        S = alt/cos(ThetaRS) #shadow length
        #calculate the angle at the center of the earth 
        ThetaP = asin(S * sin(ThetaRS)/RS)
        print "RE: ", RE, "S: ", S, "ThetaP: ", ThetaP
        lat_shadow = radians(lat) + ThetaP * cos(azimuth_rad)
        lon_shadow = radians(lon) + ThetaP * sin(azimuth_rad)* cos(abs(lat_shadow))
        
        delta = 1
        while abs(delta)>9e-10:
            old_ThetaP = ThetaP
            RS = radius_wgs84(lat_shadow)
            S = sqrt(RS**2 + RE**2 - 2 * RE * RS * cos(ThetaP))
            ThetaP = asin(S / RS * sin(ThetaRS))
            lat_shadow = radians(lat) + ThetaP * cos(azimuth_rad)
            lon_shadow = radians(lon) + ThetaP * sin(azimuth_rad)* cos(abs(lat_shadow))
            delta = ThetaP - old_ThetaP
            print "RS: ", RS, "Lat: ", degrees(lat_shadow), "Lon: ", degrees(lon_shadow), "S: ", S, "ThetaP: ", ThetaP, "Delta: ", delta
            
def get_moon_shadow_V3(in_lat, in_long, in_alt, in_time):
    #calculate the moons shadow using WGS84 geoid.
    time_zone_delta = 4
    tz = timedelta(hours = time_zone_delta)
    shadow_lat = []
    shadow_lon = []
    shadow_time = []
    #print "Input Size: ", len(in_lat)
    for lat, lon, alt, time in zip(in_lat, in_long, in_alt, in_time):
        #print "Time: ",type(time)
        #print "Lat: ", type(lat)
        #print "Long: ",type(lon)
        #print "Alt: ", type(alt)
        if isinstance(lat, str):
            lat = float(lat)
            lon = float(lon)
            alt = float(alt)
        
        if isinstance(time, datetime):
            time = time + tz
        else:
            try:
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f') + tz
            except:
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S') + tz
        #print "Time: ", time
        obs = ephem.Observer()
        obs.long, obs.lat = str(lon), str(lat)
        alt_meters = float(alt)*0.3048
        obs.elev = alt_meters
        #print "Aircraft Horizon: ", obs.horizon
        moon = ephem.Moon()
        data = {}
        date = time
        obs.date = '{year}/{month}/{day} {hour}:{minute}:{second}'.format(
            year = date.year,
            month = date.month,
            day = date.day,
            hour = date.hour,
            minute = date.minute,
            second = date.second + date.microsecond/1e6
            )
        
        
        moon.compute(obs)
        #print moon
        azimuth_rad = moon.az.real
        altitude_rad = moon.alt.real
        #print "Aircraft Lat:", lat, "Aircraft Lon: ", lon, "Aircraft Alt: ", alt, "Moon Azimuth: ", degrees(azimuth_rad), "Moon Elevation: ", degrees(altitude_rad)
        E_tgt = altitude_rad
        shad_lat = lat
        shad_lon = lon
        shad_alt = 79.0 #change this to height above ellipsoid
        alt_meters = float(shad_alt)*0.3048
        shadow = ephem.Observer()
        shadow.date = obs.date
        shadow.long, shadow.lat = str(shad_lon), str(shad_lat)
        shadow.elev = alt_meters
        moon.compute(shadow)
        shad_az_rad = moon.az.real
        shad_el_rad = moon.alt.real        
        
        #print "Shadow Lat:", shad_lat, "Shadow Lon: ", shad_lon, "Shadow Alt: ", shad_alt, "Moon Azimuth: ", degrees(shad_az_rad), "Moon Elevation: ", degrees(shad_el_rad), "Delta EL: ", degrees(shad_el_rad-altitude_rad)
        if shad_el_rad > 0.01:
            #iterate until the moon observation on the ground is the same as the moon observation from the plane.
            d_old = 0.0
            E_old = shad_el_rad
            d = 1.0
            delta_El = 1
            while abs(delta_El) > 1e-10:
                
                crs = mod(azimuth_rad+pi, 2*pi)
                shad_lat, shad_lon = lat_from_rad_d(lat, lon, crs, d)
                shadow = ephem.Observer()
                shadow.long, shadow.lat, shadow.elev, shadow.date = str(shad_lon), str(shad_lat), alt_meters, obs.date
                moon.compute(shadow)
                shad_az_rad = moon.az.real
                shad_el_rad = moon.alt.real
                E_new = shad_el_rad
            #    print "d_new: ", d
            #    print "d_old: ", d_old
            #    print "Lat: ", shad_lat
            #    print "Lon: ", shad_lon
            #    print "E_new: ", degrees(E_new)
            #    print "E_old: ", degrees(E_old)
            #    print "E_tgt: ", degrees(E_tgt)
                
                
                #m = (d - d_old)/(E_new - E_old)
                #b = d + m * E_new
                #print "m: ", m
                #print "b: ", b
                d_new = (d - d_old) / (E_new - E_old) * (E_tgt - E_old) + d_old
                delta_El = shad_el_rad - altitude_rad 
                #print "alt_meters: ", alt_meters
                #print degrees(altitude_rad)
                #print degrees(shad_el_rad)
            #    print "Delta EL: ", degrees(delta_El), "Shad_Lat: ", shad_lat, "Shad_Lon: ", shad_lon, "new_d:", d_new, "Delta_El: ", delta_El
                d_old = d
                d = d_new
                E_old = E_new
            
            #print "Aircraft Lat:", lat, "Aircraft Lon: ", lon, "Aircraft Alt: ", alt, "Moon Azimuth: ", degrees(azimuth_rad), "Moon Elevation: ", degrees(altitude_rad)
            #print "Aircraft Lat:", lat, "Aircraft Lon: ", lon, "Aircraft Alt: ", alt, "Shadow Lat:", shad_lat, "Shadow Lon: ", shad_lon, "Shadow Alt: ", shad_alt, "Moon Azimuth: ", degrees(shad_az_rad), "Moon Elevation: ", degrees(shad_el_rad), "Delta EL: ", degrees(shad_el_rad-altitude_rad), "d: ", d
            
            #Delta_El = 1
            #while abs(Delta_El)> 1e-10:
            #crs = mod(azimuth_rad+pi, 2*pi)
            #d = est_Delta_El(altitude_rad, shad_el_rad)
            #shad_lat, shad_lon = lat_from_rad_d(shad_lat, shad_lon, crs, d)
            #alt_meters = float(shad_alt)*0.3048
            #shadow = ephem.Observer()
            #shadow.long, shadow.lat, shadow.elev, shadow.date = str(shad_lon), str(shad_lat), alt_meters, obs.date
            #moon.compute(shadow)
            #shad_az_rad = moon.az.real
            #shad_el_rad = moon.alt.real
            
            
            
            #print "Moon Azimuth: ", degrees(shad_az_rad), "Moon Elevation: ", degrees(shad_el_rad)
            #Delta_El = shad_el_rad-altitude_rad
            
            
            
            
            #print "Shadow Lat:", shad_lat, "Shadow Lon: ", shad_lon, "Shadow Alt: ", shad_alt, "Moon Azimuth: ", degrees(shad_az_rad), "Moon Elevation: ", degrees(shad_el_rad), "Delta EL: ", degrees(shad_el_rad-altitude_rad)
            shadow_lat.append(shad_lat)
            shadow_lon.append(shad_lon)
            shadow_time.append(time)
    return shadow_lat, shadow_lon, shadow_time
        

        
def est_Delta_El(thetaA, thetaS):
    rmoon = 204452.0 #nautical miles to the moon
    theta1 = thetaS - thetaA
    d1 = sin(theta1)/sin(thetaS)*rmoon
    d2 = sin(theta1)/sin(thetaA)*rmoon
    d = (d1+d2)/2.0
    #d = sqrt(2*rmoon**2 - 2*rmoon**2*cos(theta1))
    print theta1, thetaS, thetaA, "D: ",d
    return d
    
           
        
        
def lat_from_rad_d(shad_lat, shad_lon, crs, d = 1):
    d_rad = d*(pi/180/60)
    lat_r = radians(shad_lat)
    lon_r = radians(shad_lon)
    lat_2_r = asin(sin(lat_r) * cos(d_rad)+cos(lat_r)*sin(d_rad)*cos(crs))
    #lat =    asin(sin(lat1 ) * cos(d    )+cos(lat1 )*sin(d    )*cos(tc ))
    dlon =  atan2(sin(crs)*sin(d_rad)*cos(lat_r), cos(d_rad)-sin(lat_r)*sin(lat_2_r))
    #dlon=  atan2(sin( tc)*sin(d    )*cos( lat1), cos(d    )-sin(lat1   )*sin(lat  ))
    #print degrees(dlon)
    lon_2_r = mod(lon_r+dlon+pi, 2*pi)-pi
    
    #shad_lon_2=mod(radians(shad_lon)-asin(sin(radians(crs))*sin(d_rad)/cos(radians(shad_lat_2)))+pi,2*pi)-pi
    #print "Shadow Lat:", degrees(lat_2_r), "Shadow Lon: ", degrees(lon_2_r)#, "Shadow Alt: ", shad_alt, "Moon Azimuth: ", degrees(shad_az_rad), "Moon Elevation: ", degrees(shad_el_rad), "Delta EL: ", degrees(shad_el_rad-altitude_rad)
    return degrees(lat_2_r), degrees(lon_2_r)
             
def radius_wgs84(lat_rad):
    #return the radius of the earth at a given latitude
    a = 6378137.0 #equator radius in meters
    b = 6356752.3142 #pole radius in meters
    ab = a*b
    sin_sq = sin(lat_rad)**2
    cos_sq = cos(lat_rad)**2
    r = ab/sqrt(a**2*sin_sq + b**2*cos_sq)
    return r


    


if __name__ == '__main__':
    in_lat = [45.0]
    in_long = [-75.0]
    in_alt = [10000]
    in_time = ['2015-03-25 20:00:12.388000']
    get_moon_shadow_V3(in_lat, in_long, in_alt, in_time)
    
    
    
    
    
    #lat = 45.5788770773
    #long = -76.0694046021
    #alt = -76.0694046021;10250
    #in_string = '2014-10-24 16:29:32.131000;45.5788770773;-76.0694046021;10250'
    #time_zone_delta = 4
    ##tz = timedelta(hours = time_zone_delta)
    #time, lat, long, alt = in_string.split(";")
    #lat = float(lat)
    ##long = float(long)
    #alt = float(alt)
    #time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f') + tz
    ##print get_moon_shadow(lat, long, alt, time)
    
    
    