import os

MASTER_DICTIONARY = "master_dictionary"
STOP_WORDS = "stop_words"

def getStopWords():
    stop_words = [] 

    files = os.listdir(os.path.join(STOP_WORDS))
    
    for file in files:
        with open(os.path.join(STOP_WORDS, file), "r") as f:
            lines = f.readlines()
            for line in lines:
                stop_words.append(line.split(" ")[0].strip())
    
    return stop_words

def getMasterDictionary():

    files = os.listdir(os.path.join(MASTER_DICTIONARY))    
    masterDictionary = {"positive_words":[], "negative_words":[]}

    with open(os.path.join(MASTER_DICTIONARY, "negative-words.txt"), "r") as f:
        lines = f.readlines()
        for line in lines:
            word = line.strip()
            if(word not in stop_words):
                masterDictionary['negative_words'].append(word)
    
    with open(os.path.join(MASTER_DICTIONARY, "positive-words.txt"), "r") as f:
        lines = f.readlines()
        for line in lines:
            word = line.strip()
            if(word not in stop_words):
                masterDictionary['positive_words'].append(line.strip())

    return masterDictionary

stop_words = getStopWords()
masterDictionary = getMasterDictionary()

