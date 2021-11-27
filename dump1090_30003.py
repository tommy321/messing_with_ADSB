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
    pi = telnetlib.Telnet('192.168.1.103','30003') #PI
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
        lat_s =  45.355406
        lon_s = -75.917406
        location = CPR_to_lat.CPR_to_LL(CPR_Lat, CPR_Lon, CPR_Format, lat_s, lon_s)
        #print location
            
            
        #print last_frame['AA'], "Type: ", Type, "SubType: ", SubType, "Altitude: ", alt
        #print "AA: ", last_frame['AA'], " Location: ", location, "Format: ", CPR_Format
        last_frame['LL'] = location
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
    filename = str(last_frame['Hex_ID']) + '.log'
    lat = last_frame['LL'][0]
    lon = last_frame['LL'][1]
    alt = last_frame['Altitude']
    line = str(datetime.datetime.now()) + ";" + str(lat) +";" + str(lon) + ";" + str(alt) + '\n' 
    print line
    
    fo = open(filename, 'a')
    fo.write(line)
    fo.close()
    
    return True


def decode_frame_data(input_data):
    split_data = input_data.split(',')
    frame_data={'MSG_TYPE':split_data[0],
                'TRANS_TYPE':split_data[1],
                'Session_ID':split_data[2],
                'Aircraft_ID':split_data[3],
                'Hex_ID':split_data[4],
                'Flight_ID':split_data[5],
                'Date_Gen':split_data[6],
                'Time_Gen':split_data[7],
                'Date_Logged':split_data[8],
                'Time_Logged':split_data[9],
                'Callsign':split_data[10],
                'Altitude':split_data[11],
                'GroundSpeed':split_data[12],
                'Track':split_data[13],
                'Lat':split_data[14],
                'Lon':split_data[15],
                'VertRate':split_data[16],
                'ModeA':split_data[17],
                'Emerg':split_data[18],
                'SPI':split_data[19],
                'OnGround':split_data[20],
                'date':datetime.datetime.now()}
    if frame_data['Lat'] != "" and frame_data['Lon'] != "":
        LL = (float(frame_data['Lat']), float(frame_data['Lon']))
        frame_data['LL'] = LL
    
    if frame_data['Altitude'] != "":
        frame_data['Altitude'] = int(frame_data['Altitude'])
        
    if frame_data['GroundSpeed'] != "":
        frame_data['GroundSpeed'] = int(frame_data['GroundSpeed'])
    
    if frame_data['Track'] != "":
        frame_data['Track'] = int(frame_data['Track'])
        
    if frame_data['VertRate'] != "":
        frame_data['VertRate'] = int(frame_data['VertRate'])
    
    
        
    return frame_data




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
    
    input_data = pi.read_until('\n')
    #print "INTPUT DATA: ", input_data
    #stripped = input_data[2].lstrip('\n*').rstrip(';')
    #print "STRIPPED: ", stripped
    #print "Pi: ", input_data, "Stripped: ", stripped
    #last_frame = last_frame.lstrip('@').rstrip().rstrip(';')
    
    #print split_data
    frame_data = decode_frame_data(input_data)
    #print frame_data
    
    if 'LL' in frame_data:
            print frame_data
            write_to_file(frame_data)
            #send_SMS.send_SMS(last_frame)
            
            
    if not add_to_kml.check_if_active(last_kml_update, timeout = datetime.timedelta(seconds = 1)):
            add_to_kml.scan_logs()
            last_kml_update = datetime.datetime.now()    
    
    
    
    
    
    