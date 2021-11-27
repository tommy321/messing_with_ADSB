import telnetlib
import re
import binascii
import CPR_to_lat
import datetime
#import add_to_kml
import KML_V2 as add_to_kml
import send_SMS



try:
    tn = telnetlib.Telnet('127.0.0.1','30002') #own PC
except:
    tn = False
try:
    pi = telnetlib.Telnet('192.168.1.106','30002') #PI
except:
    pi = False
    
print tn
print pi

def get_bits(data, bits):
    out = 0
    #print "Data: ", data
    #print data['numeric_data']
    numeric = int(data['numeric_data'])
    #print data
    #dec_data = int(data, 16)
    #print "Input: ", bin(numeric)
    #print "Bits: " , bits
    
    total_bits=data['size']
    
    #print "Total Bits: ", (total_bits)
    shift = total_bits - bits[1] 
    #print "Shift: ", shift
    mask = 2**(bits[1]-bits[0]+1)-1<<shift
    #print "Mask:  ", bin(mask)
    out = (numeric & mask) >> shift
    #print bin(out)
    return out

def get_DF(last_frame):
    DF = get_bits(last_frame, [1,5])
    return DF

def decode_17(last_frame):
    alt = 0
    CPR_Lat = 0
    CPR_Lon = 0
    CPR_Format = -1
    
    last_frame['DF'] = 17
    AA = get_bits(last_frame, [9,32])
    #print hex(AA)
    last_frame['AA'] = hex(AA)
    ME = get_bits(last_frame, [33,88])
    last_frame['ME'] = ME
    Type = get_bits(last_frame, [33,37])
    #print Type
    SubType = get_bits(last_frame, [38, 40])
    #print "Type: ", Type, "SubType: ", SubType
    #print last_frame
    
    if Type in range(9,19)+range(20,23): #Airborne position report.
        #print Type
        Altitude = get_bits(last_frame, [41,52])
        Q = (Altitude & 0b10000)>>4
        if Q == 1:
            alt = ((Altitude & 0b111111100000)>>1) | (Altitude & 0b1111)
            alt = alt * 25 - 1000
        last_frame["Alt"] = alt
        
        CPR_Lat = float(get_bits(last_frame, [55,71]))
        CPR_Lon = float(get_bits(last_frame, [72,88]))
        CPR_Format =  float(get_bits(last_frame, [54,54]))
        lat_s =  45.342491
        lon_s = -75.801656
        location = CPR_to_lat.CPR_to_LL(CPR_Lat, CPR_Lon, CPR_Format, lat_s, lon_s)
        #print location
            
            
        #print last_frame['AA'], "Type: ", Type, "SubType: ", SubType, "Altitude: ", alt
        #print "AA: ", last_frame['AA'], " Location: ", location, "Format: ", CPR_Format
        last_frame['LL'] = location
    
    if Type in range(19):
        #this message has the Baro GPS delta
        #print "Decoding GPS Delta"
        sign = float(get_bits(last_frame, [81, 81]))
        delta = float(get_bits(last_frame, [82,88]))
        print hex(AA), sign, delta
        if delta == 0:
            last_frame['Baro_GPS_delta'] = False
        else:
            Baro_GPS_delta = (delta-1.0) * 25.0
            if sign == 1:
                last_frame['Baro_GPS_delta'] = -1.0 * Baro_GPS_delta
            else:
                last_frame['Baro_GPS_delta'] = Baro_GPS_delta
        
            
        #print "Baro GPS Delta: ", last_frame['Baro_GPS_delta']
    
    if Type in range(20,23):
        #this one should have GPS alttiude.
        print "GPS Altitude"
    
    return last_frame


def decode_frame(last_frame):
    DF = get_DF(last_frame)
    decoded_frame = []
    if (DF == 4):
        #DF4 is FS, DR, UM, AC
        #get altitude code
        AC = get_bits(last_frame, [20,32])
        #print "AC: ", AC
    elif (DF == 17):
        decoded_frame = decode_17(last_frame)
            
    return decoded_frame
        


def write_to_file(last_frame):
    filename = str(last_frame['AA']).split('x')[1].rstrip('L').upper() + '.log'
    lat = last_frame['LL'][0]
    lon = last_frame['LL'][1]
    alt = last_frame['Alt']
    line = str(datetime.datetime.now()) + ";" + str(lat) +";" + str(lon) + ";" + str(alt) + '\n' 
    #print line
    
    fo = open(filename, 'a')
    fo.write(line)
    fo.close()
    
    return True







DFs_seen = []
last_frame = {'raw_data': "",
              'size': "",
              'numeric_data':""}
last_frame['raw_data'] = "SD:LJFKS"
last_kml_update = datetime.datetime.now()
while True:
    last_frame = {}
    #if pi:
    #   input_data= pi.read_until(';')
    #   print input_data
    
    #input_data= tn.read_until(';')
    
    #stripped = re.search('[@*].*;',input_data).group(0).lstrip('@').lstrip('*').rstrip(';')
    #print "Computer: ", input_data, "Stripped: ", stripped
    
    #input_data= pi.read_until(';')
    
    input_data = pi.expect([re.compile('@.*;')])
    #print "INTPUT dATA: ", input_data
    stripped = input_data[2].lstrip('\n@').rstrip(';')
    #print "STRIPPED: ", stripped
    #print "Pi: ", input_data, "Stripped: ", stripped
    #last_frame = last_frame.lstrip('@').rstrip().rstrip(';')
    
    size = len(stripped)*4
    if size == 160:
        size = 112
    elif size == 104:
        size = 56
        
    mlat = stripped[0:12]
    frame = stripped[12:]
    last_frame['mlat'] = mlat
    last_frame['raw_data'] = frame
    last_frame['size'] = size
    last_frame['numeric_data'] = int(frame, 16)
    last_frame['timestamp'] = datetime.datetime.now()
    #print last_frame
    
    numeric_frame = int(frame, 16)
    
    #print last_frame
    if numeric_frame:
        #print mlat, " ", frame, " ", numeric_frame
        DF = get_DF(last_frame)
        if DF not in DFs_seen:
            DFs_seen.append(DF)
        #print DFs_seen
        
        #print last_frame
        
        decoded_frame = decode_frame(last_frame)
        #print decoded_frame
        if 'LL' in last_frame:
            #print last_frame
            write_to_file(last_frame)
            send_SMS.send_SMS(last_frame)
        
            
            
        if not add_to_kml.check_if_active(last_kml_update, timeout = datetime.timedelta(seconds = 1)):
            add_to_kml.scan_logs()
            last_kml_update = datetime.datetime.now()
            
        #print DFs_seen
        