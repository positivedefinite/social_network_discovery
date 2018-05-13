counter     = 0
pairs       = []
altPairs    = []
lenAltPairs = []
exceptions  = []
def tweets2list(file):
    import re
    print('Counting lines...')
    number_of_tweets = sum(1 for line in file)  #this is the total number of available tweets
    print('There are '+str(number_of_tweets)+' lines in this text file. Is each line a tweet?')
    interval_size = int(number_of_tweets/10) # this is just to show progress
    
    for line in file:
        #print(line)
        counter=counter+1
        if counter%interval_size==0: # progress
            print(str(counter)+' / '+str(number_of_tweets))
            
        m = re.search(r'\t([^\t]+)\thttp[^\t]+\t([^\t]+)\t',line)
        if counter==1:
            typeHolder = type(m)
        #print(type(m))
        if type(m)==typeHolder:
            username = m.group(1)
            retweetee = re.search('RT @([^:]+)',m.group(2))
            #print(retweetee.group(1))
            try:
                retweetee = retweetee.group(1)
                print(str(username)+' '+str(retweetee.group(1)))
            except:
                if type(retweetee)!=str:
                    retweetee='NONE'
            pair = [username,retweetee]
            altPair = str(username+'|'+retweetee)
            if len(altPair)<=31: 
                pairs.append(pair)
                altPairs.append(altPair)
            else:
                exceptions.append(m)
        else:
            exceptions.append(m)
        if counter==number_of_tweets:
            break
        
    
    print('Number of captured pairs '+str(len(pairs)))
    print('Number of captured alt pairs '+str(len(altPairs)))
    print('Number of captured exceptions '+str(len(exceptions)))
    print('Maximum length of pair '+ str(max(lenAltPairs)-1))
    print('Parsing finished')
    file.close()
    return altPairs