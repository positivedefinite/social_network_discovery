# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 15:58:13 2018

@author: OP
"""
# Regexp: \n[0-9]+\t[^\t]+\t([^\t]+)\t[^\t]+\t
import opm, utils

import pandas as pd
import os.path
import networkx as nx
import matplotlib.pyplot as plt
import random, time, re, pickle

#import pydot as pydot
#import pygraphviz as pgv

def tic(times):
    times.append(time.time())
    last = len(times)-1
    print('Time elapsed from last tic: '+str(int(times[last]-times[last-1]))+' seconds')
    return times
t=[time.time()]
tic(t)

print('Part 1/5: Loading pickled pairs and sentiment.')
pickle_in = open('sam_data.pkl',"rb")
[altPairs, sentiments, number_of_tweets] = pickle.load(pickle_in)
# Part 2: Building edge weights

tic(t)
print('Part 2/5: Hashing and sorting pairs.')
[hashedPairs, sortedHashedPairs, sortedSentiments, dictionary] = utils.edgeHash(altPairs, sentiments)
# important! condition is a treshold for sentiment, can be any interval too!
print('Part 3/5: Building a sentiment dictionary.')
sentimentDict = utils.pairs2edges(sortedHashedPairs, sentiments, condition = lambda x: x>0.0)

del hashedPairs, sortedHashedPairs, sortedSentiments, altPairs, sentiments

edges_with_weights = []
print('Part 4/5: Building edge weights.')
for key in sentimentDict:
    edge = dictionary[key].split('|')+[sentimentDict[key]]
    edges_with_weights.append(edge)

del dictionary, sentimentDict
#####################################################
# Part 4: Building the graph
print('Part 5/5: Building the graph.')
G = nx.Graph()
# remove weak edges
for i in range(0,len(edges_with_weights)):
    e = edges_with_weights[i]
    if len(e)>3:
        edges_with_weights[i] = [e[0],e[1],e[3]]
G.add_weighted_edges_from(edges_with_weights)
G.remove_node('NONE')
import pickle
with open('G.pkl', 'wb') as f:
    pickle.dump(G, f)

print('Number of connected components ' +str(nx.number_connected_components(G)))
#nx.write_gml(G, "test15m.gml")
