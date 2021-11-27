import datetime
from math import pi, degrees, radians, asin, acos, tan, sin, cos
from moon import get_moon_shadow_V3
import smtplib


active_aircraft_list = []


def send_email(AA, distance):
    fromaddr = 'toms.rpi@gmail.com'
    toaddrs  = '6136978840@pcs.rogers.com'
    text = "Subject: " + AA + ": " + distance
    msg = "\r\n".join([
                       "From: user_me@gmail.com",
                       "To: user_you@gmail.com",
                       text
                       ])
    username = 'toms.rpi@gmail.com'
    password = 'dump1090_planetracker'
    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.ehlo()
    session.starttls()
    session.login(username,password)
    session.sendmail(fromaddr, toaddrs, msg)
    session.quit()
    


class Active_Aircraft_List(object):
    def __init__( self ):
        self.aircraft= []
    def __call__(self):
        return self.aircraft
    def add_aircraft(self, new):
        exists_flag = False
        for planes in self.aircraft:
            if planes['AA'] == new['AA']:
                #print "Plane Exists"
                #add the current LL to the table. 
                planes['LL_List'].append(new['LL'])
                #print "From Send SMS: ", [new['LL'][0]], [new['LL'][1]], [new['Alt']], [new['timestamp']]
                if planes.has_key('Geo_Alt'):
                    alt = planes['Geo_Alt']
                else:
                    alt = float(new['Alt'])
                shadow_lat, shadow_lon, shadow_time = get_moon_shadow_V3([new['LL'][0]], [new['LL'][1]], [alt], [new['timestamp']])
                #print shadow_lat, shadow_lon
                planes['Shadow_List'].append((shadow_lat, shadow_lon))
                exists_flag = True
        if exists_flag == False:
            new['LL_List'] = []
            new['LL_List'].append(new['LL'])
            new['Shadow_List'] = []
            new['Msg_Sent'] = False
            shadow_lat, shadow_lon, shadow_time = get_moon_shadow_V3([new['LL'][0]], [new['LL'][1]], [float(new['Alt'])], [new['timestamp']])
            #print "Shadow Lat: ", shadow_lat, "Shadow Lon: ", shadow_lon, "Time: ", shadow_time
            new['Shadow_List'].append((shadow_lat, shadow_lon))
            
            self.aircraft.append(new)
        self.purge_aircraft()
        self.calculate_course()
        self.calculate_brg()
        self.calculate_moon()
        self.calculate_XTK()
        self.calculate_Geo_Alt()
        
    def calculate_Geo_Alt(self):
        for planes in Aircraft_List():
            if planes.has_key('Alt') and planes.has_key('Baro_GPS_delta'):
                #print "Calculate Geo Alt"
                if planes['Baro_GPS_delta']:
                    planes['Geo_Alt'] = planes['Alt'] + planes['Baro_GPS_delta']
                else:
                    planes['Geo_Alt'] = False
    def calculate_course(self):
        for planes in Aircraft_List():
            if len(planes['LL_List'])>1:
                #calculate the current course of the aircraft.
                
                lon1 = radians(planes['LL_List'][0][1])
                lat1 = radians(planes['LL_List'][0][0])
                lon2 = radians(planes['LL_List'][-1][1])
                lat2 = radians(planes['LL_List'][-1][0])
                #print "lat1: ", degrees(lat1), " lon1: ", degrees(lon1), "lat2: ", degrees(lat2), "lon2: ", degrees(lon2)
                if (lon1 != lon2 and lat1 != lat2):
                    d=acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon1-lon2))
                    if sin(lon2-lon1)<0:
                        tc1=acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))
                        crs = 360.0-degrees(tc1)
                    else:
                        tc1=2*pi-acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))
                        crs = 360.0-degrees(tc1)
                    planes['CRS'] = crs
                    #print planes['AA'], " CRS: ", crs
    def calculate_brg(self):
        lat2 = radians(45.342491)
        lon2 = radians(-75.801656)
        for planes in Aircraft_List():
            lon1 = radians(planes['LL_List'][-1][1])
            lat1 = radians(planes['LL_List'][-1][0])
            d=acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon1-lon2))
            if sin(lon2-lon1)<0:
                tc1=acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))
                crs = 360.0-degrees(tc1)
            else:
                tc1=2*pi-acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))
                crs = 360.0-degrees(tc1)
            planes['BRG'] = crs
            #print planes['AA'], "BRG: ", planes['BRG']
    def purge_aircraft(self):
        #remove aircraft that haven't been seen in a while.
        temp_list = [] 
        for planes in self.aircraft:
            seen = planes['timestamp']
            timenow = datetime.datetime.now()
            timeout = datetime.timedelta(seconds = 180)
            since_seen = timenow - seen
            if since_seen < timeout: #only keep airplanes seen recently. 
                #keep only the last X lat/long in the list.
                X = 10
                planes['LL_List'] = planes['LL_List'][-X:]
                planes['Shadow_List'] = planes['Shadow_List'][-X:]
                #print len(planes['LL_List'])
                temp_list.append(planes)
        self.aircraft = temp_list
    def calculate_moon(self):
        temp_list = []
        for planes in Aircraft_List():
            #print planes['Shadow_List']
            try:
                if planes['Shadow_List'][0][1][0]:
                    #calculate the current course of the aircraft.
                    #print planes['Shadow_List']
                    lon1 = radians(planes['Shadow_List'][0][1][0])
                    lat1 = radians(planes['Shadow_List'][0][0][0])
                    lon2 = radians(planes['Shadow_List'][-1][1][0])
                    lat2 = radians(planes['Shadow_List'][-1][0][0])
                    #print "lat1: ", degrees(lat1), " lon1: ", degrees(lon1), "lat2: ", degrees(lat2), "lon2: ", degrees(lon2)
                    if (lon1 != lon2 and lat1 != lat2):
                        d=acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon1-lon2))
                        if sin(lon2-lon1)<0:
                            tc1=acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))
                            crs = 360.0-degrees(tc1)
                        else:
                            tc1=2*pi-acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))
                            crs = 360.0-degrees(tc1)
                        planes['Moon_CRS'] = crs
                        #print planes['AA'], " Moon_CRS: ", crs
                        
                    #calculate the bearing from the moon shadow to the current location
                    lat2 = radians(45.342491)
                    lon2 = radians(-75.801656)
                    lon1 = radians(planes['Shadow_List'][-1][1][0])
                    lat1 = radians(planes['Shadow_List'][-1][0][0])
                    #print "lat1: ", degrees(lat1), " lon1: ", degrees(lon1), "lat2: ", degrees(lat2), "lon2: ", degrees(lon2)
                    if (lon1 != lon2 and lat1 != lat2):
                        d=acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon1-lon2))
                        if sin(lon2-lon1)<0:
                            tc1=acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))
                            crs = 360.0-degrees(tc1)
                        else:
                            tc1=2*pi-acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))
                            crs = 360.0-degrees(tc1)
                        planes['Moon_BRG'] = crs
                        #print planes['AA'], " Moon_CRS: ", crs    
                
            except:
                a = 1
            temp_list.append(planes)
        self.aircraft = temp_list
    
    
    
    def calculate_XTK(self):
        temp_list = []
        for planes in Aircraft_List():
            if planes.has_key('CRS') and planes.has_key('Moon_CRS') and planes.has_key('Moon_BRG') and abs(planes['Moon_BRG']-planes['Moon_CRS'])<90:
                #calculate the distance from the current shadow location to the home location.
                lon1 = radians(planes['Shadow_List'][-1][1][0])
                lat1 = radians(planes['Shadow_List'][-1][0][0])
                lat2 = radians(45.342491)
                lon2 = radians(-75.801656)
                dist_AD = acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon1-lon2))
                
                
                crs_AD = radians(planes['Moon_BRG'])
                crs_AB = radians(planes['Moon_CRS'])
                
                XTD =asin(sin(dist_AD)*sin(crs_AD-crs_AB))
                distance_km = ((180*60)/pi)*XTD * 1.852
                #print "AA: ", planes['AA'], "XTK: ", distance_km
                planes['XTK'] = distance_km
            temp_list.append(planes)
        self.aircraft = temp_list
                
                
                
        
            
         
        
        
            
    #def remove_aircraft(self, ):

        
Aircraft_List = Active_Aircraft_List()        

def send_SMS(last_frame):
    #print "start SMS routine:"
    smallest_XTK = 100.0
    closest_plane = {}
    #print("Aircraft List Size:", len(Aircraft_List()))
    for planes in Aircraft_List():
        print planes['AA'], '\t', planes['Alt'], '\t', planes['Baro_GPS_delta'], '\t', planes['Geo_Alt']
        if planes.has_key('XTK'):
            if abs(planes['XTK'])<abs(smallest_XTK):
                smallest_XTK = planes['XTK']
                closest_plane = planes
            #print planes['XTK'], planes['Msg_Sent']
            if abs(planes['XTK'])<2.0 and not planes['Msg_Sent']:
                print "Sending Email."
                print "AA: ", planes['AA'], "XTK: ", planes['XTK']
                send_email(planes['AA'], str(planes['XTK']))
                planes['Msg_Sent'] = True
    if 'AA' in closest_plane:
        #print ""
        print("Closest Plane: ", closest_plane['AA'], "XTK: ", closest_plane['XTK'], "BRG: ", closest_plane['Moon_CRS'])
            
            
        #    print "AA: ", planes['AA'], " CRS: ", planes['CRS'], " MOON CRS:", planes['Moon_CRS'], "Moon BRG:", planes['Moon_BRG']
        
    #check if aircraft has more than two position points active recently active.
    
                
            
    
    #calculate the course to home position. 
    
    #check if the course to the home position is <90 degrees
    
    #check the XTE to the home position.
    
    #if XTE is less than threshold send an SMS.
    
    
    #add the aircraft to the list (replacing the last data point)
    Aircraft_List.add_aircraft(last_frame)


if __name__ == '__main__':
    
    send_email("780A36", "-2.11")
    