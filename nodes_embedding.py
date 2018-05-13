import numpy as np
import re, hashlib, pickle

pickle_in = open('paths_with_sentiment_balanced.pkl',"rb")
[paths, ps] = pickle.load(pickle_in)

split = 0.2

### PADDING
print('Padding and vocabulary')
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
    print(sentences)
    word_counts = Counter(itertools.chain(*sentences))
    # Mapping from index to word
    vocabulary_inv = [x[0] for x in word_counts.most_common()]
    # Mapping from word to index
    vocabulary = {x: i for i, x in enumerate(vocabulary_inv)}
    return [vocabulary, vocabulary_inv]

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
shuffle_indices = np.random.permutation(np.arange(len(y)))
x = x[shuffle_indices]
y = y[shuffle_indices]
train_len = int(len(x) * split)
x_train = x[:train_len]
y_train = y[:train_len]
x_test = x[train_len:]
y_test = y[train_len:]
print('Input data built! W2V')
### TRAIN WORD TO VEC!
from w2v import train_word2vec
min_word_count = 3
context = 2
embedding_dim = 30
embedding_weights = train_word2vec(np.vstack((x_train, x_test)), 'node_embeddings', vocabulary_inv, num_features=embedding_dim,
                                       min_word_count=min_word_count, context=context)

### NN
from keras.models import Model
from keras.layers import Dense, Dropout, Flatten, Input, MaxPooling1D, Convolution1D, Embedding, ZeroPadding1D
from keras.layers.merge import Concatenate
from keras import callbacks
from sklearn import metrics
# Model Hyperparameters
filter_sizes = (3, 8)
num_filters = 20 #10
dropout_prob = (0.5, 0.8)
hidden_dims = 30
batch_size = 64
num_epochs = 1
sequence_length = 3 #400
max_words = 5000
### Part 2B: Network definition & word2vec training
### make sure to delete existing word2vec model if you want to udate it
if sequence_length != x_test.shape[1]:
    sequence_length = x_test.shape[1]
print("Vocabulary Size: {:d}".format(len(vocabulary_inv)))



input_shape = (sequence_length,)

model_input = Input(shape=input_shape)

z = Embedding(len(vocabulary_inv), embedding_dim, input_length=sequence_length, name="embedding")(model_input)

z = Dropout(dropout_prob[0])(z)

# Convolutional block
conv_blocks = []
for sz in filter_sizes:
    conv = ZeroPadding1D(padding = int((sz-1)/2))(z)
    conv = Convolution1D(filters=num_filters,
                            kernel_size=sz,
                            padding="valid",
                            activation="relu",
                            strides=1)(conv)
    conv = MaxPooling1D(pool_size=2)(conv)
    conv = Flatten()(conv)
    conv_blocks.append(conv)

z = Concatenate()(conv_blocks) if len(conv_blocks) > 1 else conv_blocks[0]
z = Dropout(dropout_prob[1])(z)
z = Dense(hidden_dims, activation="relu")(z)

model_output = Dense(1, activation="sigmoid")(z)
model = Model(model_input, model_output)
model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])


# Initialize weights with word2vec

weights = np.array([v for v in embedding_weights.values()])
print("Initializing embedding layer with word2vec weights, shape", weights.shape)
embedding_layer = model.get_layer("embedding")
embedding_layer.set_weights([weights])
    
pos=0
tot=len(labels)
for label in labels:
    if label==1:
        pos += 1
print('One rule: '+str(pos/tot))

model.fit(x_train, y_train, batch_size=5, epochs=num_epochs, validation_data = (x_test, y_test), verbose=1)

model_json = model.to_json()
with open('./models/'+'nodes'+'_json'+'.json','w') as json_file:
	json_file.write(model_json)
	##Serialize model weights to HDF5
model.save_weights('./models/'+'nodes'+'_weights'+'.h5')
print('Model saved!!')

val_accu = model.evaluate(x_test,y_test,verbose = 0)
print("Accuracy = " + str(val_accu[1]))

y_confuse = model.predict(x_test,batch_size = batch_size,verbose = 1)
for i in range(len(y_confuse)):
    if y_confuse[i]>0.5:
        y_confuse[i] = 1
    else:
        y_confuse[i] = 0

confuse_matrix = metrics.confusion_matrix(y_test, y_confuse)
print("\nConfusion Matrix:")
print(str(confuse_matrix))
