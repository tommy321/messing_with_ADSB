import json
import CPR_to_lat

merge_fname = 'E:\\workspace\\ADSB\\1090_logs\\combined.log'


def get_bits(data, bits):
    #print("GetDF:")
    out = 0
    #print "Data: ", data
    #print data['numeric_data']
    numeric = int(data[12:], 16)
    #print data
    #dec_data = int(data, 16)
    #print "Input: ", bin(numeric)
    #print "Bits: " , bits
    
    total_bits=(len(data)-12)*4
    #print "Total Bits: ", (total_bits)
    shift = total_bits - bits[1] 
    #print "Shift: ", shift
    mask = 2**(bits[1]-bits[0]+1)-1<<shift
    #print "       ", bin(numeric)
    #print "Mask:  ", bin(mask)
    out = (numeric & mask) >> shift
    #print out
    return out

def get_DF(last_frame):
    DF = get_bits(last_frame, [1,5])
    return DF



def decode_frame(last_frame):
    decoded_frame = {}
    DF = get_DF(last_frame)
    #print(DF)
    decoded_frame['DF'] = DF
    #if (DF == 4):
        #DF4 is FS, DR, UM, AC
        #get altitude code
    #    AC = get_bits(last_frame, [20,32])
        #print "AC: ", AC
    if (DF == 17):
        decoded_frame.update(decode_17(last_frame))
            
    return decoded_frame

def decode_17(last_frame):
    decoded_data = {}
    alt = 0
    CPR_Lat = 0
    CPR_Lon = 0
    CPR_Format = -1
    
    
    AA = get_bits(last_frame, [9,32])
    #print hex(AA)
    decoded_data['AA'] = hex(AA)
    ME = get_bits(last_frame, [33,88])
    decoded_data['ME'] = ME
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
        decoded_data["Alt"] = alt
        
        CPR_Lat = float(get_bits(last_frame, [55,71]))
        CPR_Lon = float(get_bits(last_frame, [72,88]))
        CPR_Format =  float(get_bits(last_frame, [54,54]))
        lat_s =  45.342491
        lon_s = -75.801656
        location = CPR_to_lat.CPR_to_LL(CPR_Lat, CPR_Lon, CPR_Format, lat_s, lon_s)
        #print location
            
            
        #print last_frame['AA'], "Type: ", Type, "SubType: ", SubType, "Altitude: ", alt
        #print "AA: ", last_frame['AA'], " Location: ", location, "Format: ", CPR_Format
        decoded_data['LL'] = location
    
    if Type in range(19):
        #this message has the Baro GPS delta
        #print "Decoding GPS Delta"
        sign = float(get_bits(last_frame, [81, 81]))
        delta = float(get_bits(last_frame, [82,88]))
        #print hex(AA), sign, delta
        if delta == 0:
            decoded_data['Baro_GPS_delta'] = False
        else:
            Baro_GPS_delta = (delta-1.0) * 25.0
            if sign == 1:
                decoded_data['Baro_GPS_delta'] = -1.0 * Baro_GPS_delta
            else:
                decoded_data['Baro_GPS_delta'] = Baro_GPS_delta
        
            
        #print "Baro GPS Delta: ", last_frame['Baro_GPS_delta']
    
    if Type in range(20,23):
        #this one should have GPS alttiude.
        print "GPS Altitude"
    
    return decoded_data




if __name__ == '__main__':
    #do this stuff when run standalone
    merge_fname = 'E:\\workspace\\ADSB\\1090_logs\\combined.log'
    merge_file = open(merge_fname, 'r')
    
    #test Flags
    DF_OK = True
    AA_OK = True
    
    
    for line in merge_file:
        data = line.split(';')
        #print(data)
        date_string = data[0]
        raw_frame = data[1].strip('@')
        #print("Raw Frame: "+ raw_frame)
        truth_data = json.loads(data[2])
        decoded_data = decode_frame(raw_frame)
        #print decoded_data, truth_data
        
        #check DF decoding
        test_key = "DF " + str(decoded_data['DF'])
        #print(test_key)
        
        if not truth_data.has_key(test_key):
            DF_OK = False
            
        #check AA decoding
        if decoded_data.has_key("AA"):
            AA_OK = True
            #print(decoded_data['AA'], truth_data['ICAO Address'])
            test_AA = str(decoded_data['AA']).strip("0x").strip("L")
            if not test_AA == truth_data['ICAO Address']:
                print("AA NotOK")
                print(test_AA, truth_data['ICAO Address'])
                AA_OK = False
                
    
    if DF_OK:
        print("All DF OK")
    if AA_OK:
        print("All AA OK")
    
            
        