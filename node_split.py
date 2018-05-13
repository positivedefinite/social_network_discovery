import numpy as np
import re, hashlib, pickle
#cd C:\Users\OP\OneDrive\APG\code\ingress
file_out = 'training_data2.pkl'
pickle_in = open('paths_balanced_all_len1.pkl',"rb")
[paths, ps, pi] = pickle.load(pickle_in)

split = 0.5

### PADDING
print('Padding')
maxLen = 0
for i in range(0,len(paths)):
    if len(paths[i])>maxLen:
        maxLen = len(paths[i])
for i in range(0,len(paths)):
    if len(paths[i])<maxLen:
        diff = maxLen-len(paths[i])
        for j in range(0,diff):
            paths[i].append("<PAD/>")
### VOCABULARY        
def build_vocab(sentences):
    from collections import Counter
    import itertools
    """
    Builds a vocabulary mapping from word to index based on the sentences.
    Returns vocabulary mapping and inverse vocabulary mapping.
    """
    # Build 
    #print(sentences)
    word_counts = Counter(itertools.chain(*sentences))
    # Mapping from index to word
    vocabulary_inv = [x[0] for x in word_counts.most_common()]
    # Mapping from word to index
    vocabulary = {x: i for i, x in enumerate(vocabulary_inv)}
    return [vocabulary, vocabulary_inv]
print('Vocabulary')
[vocabulary, vocabulary_inv_list] = build_vocab(paths)
### Dummy labels
'''
labels = []
for path in paths:
    labels.append(random.randint(0,1))
'''
labels = []
for score in ps:
    fscore = float(score)
    if fscore>0.5:
        labels.append(1)
    if fscore<=0.5:
        labels.append(0)
### build np data
def build_input_data(sentences, labels, vocabulary):
    """
    Maps sentencs and labels to vectors based on a vocabulary.
    """
    x = np.array([[vocabulary[word] for word in sentence] for sentence in sentences])
    y = np.array(labels)
    return [x, y]
[x, y] = build_input_data(paths, labels, vocabulary)
### transform to training data
vocabulary_inv = {key: value for key, value in enumerate(vocabulary_inv_list)}
'''
shuffle_indices = np.random.permutation(np.arange(len(y)))
x = x[shuffle_indices]
y = y[shuffle_indices]
train_len = int(len(x) * split)
x_train = x[:train_len]
y_train = y[:train_len]
x_test = x[train_len:]
y_test = y[train_len:]
'''
import random
li = pi
percentage_of_training = split
set_number = 0
assignment = [set_number]

for i in range(1,len(li)):
    if li[i-1]==li[i]:
        assignment.append(set_number)
    else:
        draw = random.random()
        if draw>=percentage_of_training:
            set_number = 0
        else:
            set_number = 1
        assignment.append(set_number)
        
x_train = []
y_train = []
x_test = []
y_test = []      
                
for i in range(0,len(x)):
    if assignment[i]==0:
        x_test.append(x[i])
        y_test.append(y[i])
    elif assignment[i]==1:
        x_train.append(x[i])
        y_train.append(y[i])
    else:
        print('dafuq')
        
x_train = np.asarray(x_train)
x_test = np.asarray(x_test)
y_train = np.asarray(y_train)
y_test = np.asarray(y_test)

#for i in range(0,len(y_train)):
    #if y_train

with open(file_out, 'wb') as f:
    pickle.dump([x_train, x_test, y_train ,y_test, vocabulary_inv, labels], f)
    ######

inspection= []
    
for i in range(0,len(pi)):
    inspection.append([pi[i],assignment[i]])
    
for i in range(0,len(inspection)-1):
    if inspection[i][0]==inspection[i+1][0] and inspection[i][1]!=inspection[i+1][1]:
        print('fuck')