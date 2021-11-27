import glob
import os


log_file_folder = 'E:\workspace\ADSB\*.log'
files = glob.glob(log_file_folder) #scan whole folder
print files


#scrub the *Reg line out of all the files
for fname in files:
    newfile = ''
    file = open(fname, 'r')
    for line in file:
            #print line
            if line.startswith('*'):
                print line
                if line.startswith('*Reg:'):
                    ident = line.lstrip('*Reg:')
                    check_internet_for_ident = False
            else:
                newfile = newfile+line
    file.close()
    file = open(fname, 'w')
    print fname
    file.write(newfile)
    file.close()
    
    
    
                
                    
            