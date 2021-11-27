import pickle
import json

test_fname = 'E:\\workspace\\ADSB\\1090_logs\\test_log.log'
truth_fname = 'E:\\workspace\\ADSB\\1090_logs\\dump1090.log'
merge_fname = 'E:\\workspace\\ADSB\\1090_logs\\combined.log'

def truth_data_to_dict(frame_data):
    #print("truth_data_to_dict")
    #print(frame_data)
    truth_data = {}
    frame_data = iter(frame_data.splitlines())
    #print("here1")
    for line in frame_data:
        if line.startswith('@'):
            frame = line.strip(';').upper()
            #print("here2")
        if ':' in line:
            #print("here3")
            item = line.split(':')
            key = item[0].strip()
            value = item[1].strip()
            truth_data[key] = value
        
            
    #print("here4")
    #print truth_data
    return frame, truth_data

def old_get_truth_data(truth_fname):
    #print("here5")
    truth_data = {}
    truth_file = open(truth_fname, 'r')
    for line in truth_file:
        
        if line.startswith('@'):
            #print("here9")
            #print(line)
            #print(frame + "\t" + line)
            frame_data = line
            
            while len(line)>1:
                try:
                    line = truth_file.next()
                    #print(line)
                except:
                    #print("done reading data")
                    break
                frame_data += line
            #print(frame_data)
            #print("here6")
            frame, data = truth_data_to_dict(frame_data)
            #print('here7')
            truth_data[frame] = data
            #print('here8')
            if len(truth_data.keys())%1000 == 0:
                print(len(truth_data.keys()))
           
    truth_file.close()
    #write the dictionary to a pickle file
    #print("Writing to a pickle file")
    #pickle.dump(truth_data, open("truth_dict.p", 'wb'))
    #print("Wrote file")
    return truth_data

def get_truth_data(test_frame, truth_fname):
    #print("here5")
    data = False
    truth_file = open(truth_fname, 'r')
    for line in truth_file:
        #print(line)
        if line.startswith('@'):
            #print("here9")
            #print(test_frame + '\t' + line.upper())
            if test_frame in line.upper():
                #print(test_frame + '\t' + line)
                frame_data = line
                while len(line)>1:
                    line = truth_file.next()
                        #print(line)
                    #except:
                        #print("done reading data")
                    #    break
                    frame_data += line
                #print(frame_data)
                frame, data = truth_data_to_dict(frame_data)
                #print(data)
                #print('here7')
                #print('here8')
                
    truth_file.close()
        #write the dictionary to a pickle file
        #print("Writing to a pickle file")
        #pickle.dump(truth_data, open("truth_dict.p", 'wb'))
        #print("Wrote file")
    return data
                    
                
#truth_dict = get_truth_data(truth_fname)
#print("Number of keys:") 
#print(len(truth_dict.keys()))        
    
test_file = open(test_fname, 'r')
out_file = open(merge_fname, 'w')
for line in test_file:
    test_data = line.split(';')
    if len(test_data)==3:
        test_frame = test_data[1]
        print("Looking up:" + test_frame)
        truth_data = get_truth_data(test_frame, truth_fname)
        if truth_data:
            out_line = line.strip() + json.dumps(truth_data) + '\n'
            print(out_line)
            out_file.write(out_line)
            
        
        #print(test_frame + '\t' + str(truth_data))
        
    
    
    
