"""
Oskar Person's math module
functions:
    hash
    round
    binarySearch
"""
import math

def round(v):

    if v-math.floor(v)<0.5:
        v=math.floor(v)
    else:
        v=math.ceil(v)
    
    return v


def binarySearch(a, val):
    #print(a)
    step = round(len(a)/2)
    p = step
    counter = 1
    isFound = False
    #print('[step, index, found value]')
    #print([counter,p , step])
    while (round(step)>=1 and p>=0 and p<=(len(a)-1)): # and a[p]!=p
        #print([counter,p ,a[p], step])
        if a[p]==val:
            isFound = True
            break
        if a[p]<val:
            p = p+round(step/2)
        elif a[p]>val:
            p = p-round(step/2)
        #print([counter,p ,'?', step])
        step = step/2
        counter = counter +1
    return [isFound, p]

def hash(someList):
    '''
    someList must be str
    '''
    import hashlib
    hashed = []
    for element in someList:
        if type(element)!=str:
            element=str(element)
        hashed.append(hashlib.sha1(element.encode("utf-8") ).hexdigest())
    return hashed