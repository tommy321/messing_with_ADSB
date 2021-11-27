import math


def NL(lat): 
    NZ  = 15.0
    pi = math.pi
    den = math.cos(pi/180.0 * abs(lat))**2
    num = 1-math.cos(pi/2/NZ)
    first = 1 - num/den
    second = math.acos(first)
    third = second**-1
    fourth = 2*pi*third
    NL = math.floor(fourth)
    return NL
    


def Dlat_i(i):
    NZ = 15.0
    Dlat_i = 360.0/(4.0*NZ-i)
    return Dlat_i

def j(lat_s, Dlat_i, YZ):
    Nb = 17.0
    #print "Nb: ", Nb
    first = lat_s/Dlat_i
    #print "first: ", first
    second = 0.5+ (lat_s%Dlat_i)/Dlat_i - YZ/2.0**Nb
    #print "second: ", second 
    j = math.floor(first) + math.floor(second)
    #print "j: ", j
    return j

def Rlat_i(j, Dlat_i, YZ):
    Nb = 17.0
    Rlat_i = Dlat_i*(j + YZ/2**Nb)
    return Rlat_i

def DLon_i(Rlat, i):
    nl = NL(Rlat)
    
    #print "NL: ", type(nl)
    check = nl-i
    #print "check: ", check
    if check>0:
        Dlon_i = 360.0/(check)
    elif check == 0:
        Dlon_i = 360.0
    #print "Dlon_i: ", Dlon_i
    return Dlon_i



def CPR_to_LL(CPR_Lat, CPR_Lon, Format, lat_s, lon_s):
    YZ = CPR_Lat
    XZ = CPR_Lon
    #print "CPR_Lat: ", CPR_Lat
    #print "CPR_Lon: ", CPR_Lon
    #print "Format: ", Format
    Dlat = Dlat_i(Format)
    #print "Dlat: ", Dlat
    
    J = j(lat_s, Dlat, YZ)
    #print "j: ", J
    
    Rlat = Rlat_i(J, Dlat, YZ)
    #print "RLat: ", Rlat
    
    nl = NL(Rlat)
    #print "NL: ", nl
    
    Dlon = DLon_i(Rlat, Format)
    #print "Dlon: ", Dlon
    
    m = j(lon_s, Dlon, XZ)
    #print "m: ", m
    
    
    Rlon = Rlat_i(m, Dlon, XZ)
    #print "Rlon: ", Rlon

    return (Rlat, Rlon)





#CPR_Lat = 56138.0
#CPR_Lon = 47590.0
#Format = 1.0


#YZ = CPR_Lat
#XZ = CPR_Lon

#reference point
#lat_s =  45.355406
#lon_s = -75.917406
#print CPR_to_LL(CPR_Lat, CPR_Lon, Format, lat_s, lon_s)


