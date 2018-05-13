import numpy as np
import re, hashlib, pickle
# takes raw tweets as inputs, returns paths to leaf nodes if 
min_path_length = 3
number_of_tweets = 15000000
file_out = 'paths_balanced_'+str(number_of_tweets)+'_min'+str(min_path_length)'.pkl'
file = 'O:/sam_data/sam.tsv'
file = open(file, "r", encoding = 'utf-8')
print('Counting lines...')

if number_of_tweets==0:
    #this is the total number of available tweets which doesn't work for some reason
    number_of_tweets = sum(1 for line in file)  
print('There are '+str(number_of_tweets)+' lines in this text file. Is each line a tweet?')
interval_size = int(number_of_tweets/10) # this is just to show progress

posTresh = 0.641
negTresh = 0.640

# there are quite some garbage lists here
counter     = 0
pairs       = []
altPairs    = []
pairsWithSentiment = []
lenAltPairs = []
exceptions  = []
sentiments = []
hashes = []

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
        msgsearch = re.search('T @([^:]+): ([^\t]+)',m.group(3))
        
        #print(retweetee.group(1))
        try:
            sentiment = m.group(1)
            retweetee = msgsearch.group(1)
            #print(str(username)+' '+str(retweetee))
        except:
            if type(retweetee)!=str:
                retweetee='NONE'
        try:
            msg = msgsearch.group(2)
        except:
            msg = m.group(3)
        #, m.group(3))
        #print(pair)
        msgHash = hashlib.sha1(msg.encode("utf-8")).hexdigest()
        
        #print(msg[0:30],msgHash)
        sender = retweetee
        receiver = username
        
        pair = [msgHash, str(sender), str(receiver)]
        hashes.append(msgHash)
        pairs.append(pair)
        sentiments.append(sentiment)
        exceptions.append(m)
    else:
        exceptions.append(m)
    #print([username, retweetee, sentiment])
    if counter==number_of_tweets:
        break
    
print('Hashing.')
order = sorted(range(len(hashes)), key=lambda k: hashes[k])
sortedHashes = []
sortedPairs = []
sortedSentiments = []
for i in order:
    sortedHashes.append(hashes[i])
    sortedPairs.append(pairs[i])
    sortedSentiments.append(sentiments[i])
    
#for pair in sortedPairs:
    #print(pair[0][::5],pair[1],pair[2])
print('Building trees.')    
del order, hashes, pairs, sentiments
trees = []
s = []
bucket = []
counter = 0
for i in range(0,len(sortedPairs)-1):

    leadingPair = sortedPairs[i]
    followingPair = sortedPairs[i+1]
    #print(leadingPair,followingPair)
    if leadingPair[0]==followingPair[0] and (float(sortedSentiments[i])>posTresh or float(sortedSentiments[i])<negTresh): #if following hashes match
        counter += 1
        bucket.append([leadingPair[1],leadingPair[2]])
        #print(bucket)
    else:
        trees.append(bucket)
        s.append(sortedSentiments[i])
        bucket = []
del sortedHashes, sortedSentiments, sortedPairs

### pickle
'''
with open('temp_sortedHashes.pkl', 'wb') as f:
    pickle.dump(sortedHashes, f)

'''
### add edges
import networkx as nx

paths = []
ps = []
print('Building paths.')
tree_counter = 0
for i in range(0,len(trees)):
    tree = trees[i]
    if len(tree)>10: # take only trees bigger than 10
        import random
        if random.random()>0.99: #once every 100 times print progress
            print(str(i)+'/'+str(len(trees)))
        tree_counter += 1
        G = nx.Graph()
        G.add_edges_from(tree)
        creator = []
        endpoints = []
        maxDeg = 0
        for node in G.nodes():
            deg = G.degree(node)
            if deg==1:
                endpoints.append(node)
            if deg>maxDeg:
                creator = node
        for endpoint in endpoints:
            try:
                p = nx.dijkstra_path(G, creator, endpoint)
                if len(p)>min_path_length:
                    paths.append(p)
                    ps.append(s[i])
            except:
                continue
                #print('no path')

del endpoints, creator, G
print("There were "+str(tree_counter)+" trees built.")
temp_ps = []
temp_paths = []
posCounter = 0
for i in range(0,len(paths)):
    if float(ps[i])>=posTresh:
        posCounter +=1
negCounter = len(paths) - posCounter
import random
probability = negCounter/posCounter

for i in range(0,len(paths)):
    if float(ps[i])<negTresh:# all neg are taken
        temp_ps.append(ps[i])
        temp_paths.append(paths[i])
    elif random.random()<probability:
        temp_ps.append(ps[i])
        temp_paths.append(paths[i])

with open(file_out, 'wb') as f:
    pickle.dump([temp_paths,temp_ps], f)

posCounter = 0
for i in range(0,len(temp_paths)):
    if float(temp_ps[i])>=posTresh:
        posCounter +=1
negCounter = len(temp_paths) - posCounter
print(posCounter/len(temp_ps),negCounter/len(temp_ps), len(temp_ps))