import telnetlib
import binascii

def get_bits(data, bits):
    out = 0
    #print data
    #dec_data = int(data, 16)
    print "Input: ", bin(data)
    #print "Bits: " , bits
    
    total_bits=len(bin(data))
    print "Total Bits: ", (total_bits)
    shift = total_bits - bits[1] 
    #print "Shift: ", shift
    mask = 2**(bits[1]-bits[0]+1)-1<<shift
    print "Mask:  ", bin(mask)
    out = (data & mask) >> shift
    #print bin(out)
    return out
    
    
    

def decode_frame_5(frame_data):
    frame = {}
    hex_data = frame_data.decode('hex')
    #print frame_data
    numeric_frame = bytearray(hex_data)
    #print frame_data
    #print str(numeric_frame)
    #FS
    
    #DR
    #bits 20 - 32
    
    
    #UM
    
    #ID
    #print len(numeric_frame)
    #print hex(numeric_frame[2]), hex(numeric_frame[3])
    ID = numeric_frame[3]
    D4 = ID << 2 & 0x4
    B4 = ID << 1 & 0x4
    D2 = ID >> 1 & 0x2
    B2 = ID >> 2 & 0x2
    D1 = ID >> 4 & 0x1
    B1 = ID >> 5 & 0x1
    A4 = ID >> 5 & 0x4
    ID = numeric_frame[2]
    C4 = ID << 2 & 0x4
    A2 = ID >> 0 & 0x2
    C2 = ID >> 1 & 0x2
    A1 = ID >> 3 & 0x1
    C1 = ID >> 4 & 0x1
    
    A = A4 | A2 | A1
    B = B4 | B2 | B1
    C = C4 | C2 | C1
    D = D4 | D2 | D1
    ID = A*1000 + B*100 + C*10 + D
    #if ID == 1052 | ID == 1200 | ID == 2404:
    #print ID
    
    #print "ID: " + str(A)+ str(B)+ str(C)+ str(D) #+ " AP: " + binascii.hexlify(numeric_frame[5:7])
    
    AP = binascii.hexlify(numeric_frame[5:7])
    #print frame
    frame["DF"] = 5
    frame["ID"] = ID
    frame["AP"] = AP
    return frame


def decode_frame_11(frame_data):
    #decode CA - 5-8
    frame = {}
    hex_data = frame_data.decode('hex')
    numeric_frame = bytearray(hex_data)
    
    #CA
    CA = (numeric_frame[0] & 7)
    #print "CA: " + str(CA)
    
    #AA - ICAO Code
    #bits 9-32 
    AA = (frame_data[2:8])
    #print binascii.hexlify(hex_data) + " " + "AA: " + str(AA)
    
    #PI
    #bits 
    PI = (frame_data[8:])
    #print "PI: " + str(PI)
    
    frame["DF"] = 11
    frame["CA"] = CA
    frame["AA"] = AA
    frame["PI"] = PI
    return frame

def decode_frame_17(frame_data):
    frame = {}
    #print len(frame_data)
    #print binascii.hexlify(frame_data)
    AA = (frame_data[2:8])
    
    ME = get_bits(frame_data, [33,37])
    print bin(int(frame_data,16))
    print bin(ME)
    #print "AA: " + str(AA) + " ME: " + str(ME)
    return frame


def decode_frame(frame_data):
    frame = {}
    df = get_DF(frame_data)
    print df
    
    if df == 11:
        #print df
        #print frame_data
        frame = decode_frame_11(frame_data)
    #elif df == 5:
    #    frame = decode_frame_5(frame_data)
    #elif df == 17:
    #    frame = decode_frame_17(frame_data)
    
    return frame


def get_DF(data):
    #get the DF format number from a frame
    #print data
    #hex_data = data.decode('hex')
    #numeric_frame = bytearray(hex_data)
    #print "{0:x}".format(numeric_frame[0])
    #df is the first 5 bits:
    df = get_bits(data, [1,5])
    #df = (numeric_frame[0] & 0xF8) >>3
    #if df>23:
    #    df = 24
    #print df
    return df

tn = telnetlib.Telnet('127.0.0.1','47806')
print tn

while True:
    binary = ''
    last_frame = tn.read_until('\n')
    last_frame = last_frame.lstrip('*').rstrip().rstrip(';')
    #print int(last_frame,16)
    #test get bits:
    #temp = "ADFEEACB"
    
    #out = get_bits(temp, [6,12])
    #print out
    #print last_frame
    if last_frame:
        frame = decode_frame(int(last_frame,16))
        #if frame:
        #    print frame
        #if DF == 11: #ALL-CALL
        #    print last_frame
    
    numeric_frame = int(last_frame[1:-3],16)
    #print len(bytearray(last_frame))
    bin_format = "{0:b}".format(numeric_frame)
    #print len(bin_format)
    #print format
    #if format == "01011":
    #    print numeric_frame
    #print "{0:b}".format(nmeric_frame)[1:5]
    #print last_frame
    
