
def tweets2list(file, number_of_tweets):
    import re
    file = open(file, "r", encoding = 'utf-8')
    print('Counting lines...')
    if number_of_tweets==0:
        number_of_tweets = sum(1 for line in file)  #this is the total number of available tweets
    print('There are '+str(number_of_tweets)+' lines in this text file. Is each line a tweet?')
    interval_size = int(number_of_tweets/10) # this is just to show progress
    
    
    # there are quite some garbage lists here
    counter     = 0
    pairs       = []
    altPairs    = []
    pairsWithSentiment = []
    lenAltPairs = []
    exceptions  = []
    sentiments = []
    
    for line in file:
        #print(line)
        counter=counter+1
        if counter%interval_size==0:
            print(str(counter)+' / '+str(number_of_tweets))
        #m = re.search(r'\t([^\t]+)\thttp[^\t]+\t([^\t]+)\t',line)
        m = re.search(r'([0-9]\.[0-9]+)\t[^\t]+\t[^\t]+\t[^\t]+\t([^\t]+)\thttp[^\t]+\t([^\t]+)\t',line)
        if counter==1:
            typeHolder = type(m)
        #print(type(m))
        if type(m)==typeHolder:
            username = m.group(2)
            retweetee = re.search('RT @([^:]+)',m.group(3))
            #print(retweetee.group(1))
            try:
                sentiment = m.group(1)
                retweetee = retweetee.group(1)
                print(str(username)+' '+str(retweetee.group(1)))
            except:
                if type(retweetee)!=str:
                    retweetee='NONE'
            pair = [username,retweetee]
            altPair = str(username+'|'+retweetee)# pairs are joined by "|" sign
            if len(altPair)<=31: 
                altPairs.append(altPair)
                lenAltPairs.append(len(altPair))
                pairsWithSentiment.append(altPair+'|'+sentiment)
                sentiments.append(sentiment)
            else:
                exceptions.append(m)
        else:
            exceptions.append(m)
        #print([username, retweetee, sentiment])
        if counter==number_of_tweets:
            break
        
    
    print('Number of captured joined pairs '+str(len(altPairs))) # pairs are joined by "|" sign
    print('Number of captured exceptions '+str(len(exceptions)))
    print('Maximum length of pair '+ str(max(lenAltPairs)-1))
    print('Parsing finished')
    file.close()
    return [altPairs, sentiments, number_of_tweets]

def edgeHash(altPairs, sentiments):
    import opm
    from collections import Counter
    
    print('Counting duplicates...')
    counters = Counter(altPairs)
    #print(Counter(altPairs).keys()) # equals to list(set(words))
    #print(counters) # counts the elements' frequenc
    altPairsCounted = []
    
    
    for i in range(0,len(altPairs)):
        #connection = altPairs[i].split('|')+[counters[altPairs[i]]]
        altPairCounted = altPairs[i]+'|'+str(counters[altPairs[i]])
        #connections.append(connection)
        altPairsCounted.append(altPairCounted)
        
    print('Hashing triples...')
    hashedPairs = opm.hash(altPairs)
            
    dictionary = {}
    # [hashedTriples, order, sentiments]
    for i in range(0,len(hashedPairs)):
        dictionary[hashedPairs[i]]=altPairs[i]
        
    order = sorted(range(len(hashedPairs)), key=lambda k: hashedPairs[k])
    
    sortedHashedPairs = []
    sortedSentiments = []
    for i in order:
        sortedHashedPairs.append(hashedPairs[i])
        sortedSentiments.append(sentiments[i])
    print('Hashing and sorting completed.')
    return [hashedPairs, sortedHashedPairs, sortedSentiments, dictionary]

def pairs2edges(sortedHashedPairs, sentiments, condition):

    sentimentDict = {}
    memory = float(sentiments[0])
    count = 1
    
    condition = lambda x: x>0.7
    
    for i in range(1,len(sortedHashedPairs)):
        id = sortedHashedPairs[i]
        if condition(float(sentiments[i])):
            if sortedHashedPairs[i-1]==sortedHashedPairs[i]:
                memory = memory + float(sentiments[i])
                count = count + 1
            else:
                sentimentDict[id] = memory#/count # average sentiment!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                memory = float(sentiments[i])
                count = 1
                #memory
                #print('bingo')
    return sentimentDict

def dict2list(ranks):  
    rank_list = []
    for rank in ranks:
        rank_list.append([rank,ranks[rank]])
    def takeSecond(elem):
        return elem[1]
    rank_list.sort(key=takeSecond)
    return rank_list

def extractPartition(p, graph, partition):
    toRemove = []
    graph2 = graph
    for node in graph.nodes():
        if partition[node]!=p:
            toRemove.append(node)
    for node in toRemove:
        graph2.remove_node(node)
    return graph2

#[pairs, sentiments] = tweets2list('O:/sam_data/sam.tsv')