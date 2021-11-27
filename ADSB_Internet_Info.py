import urllib
import urllib2
from bs4 import BeautifulSoup as bs
import re
import glob
import os
import cookielib



def get_registration(icao_hex):
    if icao_hex.startswith("A") or icao_hex.startswith("C"):
        url = "http://www.avionictools.com/icao.php"
        values = {'type' : '3',
                  'data' : icao_hex,
                  'strap' : '0'}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = bs(response.read())
        #print the_page.prettify()
        tds = the_page.find('tr', {'height' : '200'})
        #print tds
        trs = tds.find("td")
        reg = trs.text.split('Hex:')
        #print reg[0]
        if len(reg[0])<3:
            return icao_hex
        registration = reg[0]    
        if registration.startswith("C"):
            registration = registration[0] + "-" + registration[1:]
        return registration
    else:
        return icao_hex

def get_TC_data(reg):
    
    cookie_jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
    urllib2.install_opener(opener)
    
    # acquire cookie
    url_1 = "http://wwwapps2.tc.gc.ca/Saf-Sec-Sur/2/ccarcs/aspscripts/en/quicksearch.asp"
    req = urllib2.Request(url_1)
    rsp = urllib2.urlopen(req)
    

    # do POST
    url_2 = "http://wwwapps2.tc.gc.ca/Saf-Sec-Sur/2/ccarcs/aspscripts/en/quicksearch.asp"
    values = {'x_reset':'Y',
              'x_typeofaction':1,
              'x_Mark':reg,
              'x_searchtype':1,
              'x_commonname':'',
              'x_commonnamesearchtype':3,
              'x_modelname':'',
              'x_modelnamesearchtype':3,
              'x_serialnumber':'',
              'x_serialnumbersearchtype':3,
              'x_ownername':'',
              'x_ownernamesearchtype':3,
              'submit':'Search'}
    data = urllib.urlencode(values)
    req = urllib2.Request(url_2, data)
    rsp = urllib2.urlopen(req)
    content = rsp.read()
    print content
    
    #url = "http://wwwapps2.tc.gc.ca/Saf-Sec-Sur/2/ccarcs/aspscripts/en/quicksearch.asp"
    
    #data = urllib.urlencode(values)
    #req = urllib2.Request(url, data)
    #print data
    #response = urllib2.urlopen(req)
    
    #the_page = bs(response.read())
    #print response.msg
    #print the_page

if __name__ == '__main__':
    get_TC_data('FBQN')
    #do this stuff when run standalone
    #log_file_folder = 'E:\workspace\ADSB\*.log'
    
    #files = glob.glob(log_file_folder)
    
    #for fname in files:
        #print fname
        #ident = os.path.split(fname)[1].split('.')[0]
        #print get_registration(ident)
        