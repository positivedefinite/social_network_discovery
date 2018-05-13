
#################################################
#Part 1: Parsing the tweets into a list of [user,user]

import utils
file = 'O:/sam_data/sam.tsv'
[altPairs, sentiments, number_of_tweets] = utils.tweets2list(file, 15015772)
import pickle
with open('sam_data.pkl', 'wb') as f:
    pickle.dump([altPairs, sentiments, number_of_tweets], f)
tic(t)

#####################################################