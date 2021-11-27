import telnetlib
import re


pi = telnetlib.Telnet('192.168.0.107','30002') #PI


def get_telnet_data(pi):
    #input_data = pi.read_eager()
    input_data = pi.expect([re.compile('@.*;')])
    return input_data
    
    
    


print pi
while True:
    print get_telnet_data(pi)
    