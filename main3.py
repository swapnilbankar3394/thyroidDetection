import data
from nltk import word_tokenize
import os
import string
import nltk
import syllables
import re
import pandas as pd
# nltk.download('punkt')


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

FILES = "scraped"

stop_words = getStopWords()
masterDictionary = getMasterDictionary()


def cleanText(text):

    whole_text = []
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)

    tokens = word_tokenize(text)

    for token in tokens:
        if(token not in stop_words):
            whole_text.append(token)

    return whole_text, len(whole_text)



def analytics(text, no_of_words):

    positive_words = masterDictionary['positive_words']
    negative_words = masterDictionary['negative_words']

    # we are counting total number of characters in each word here to minimize number of iterations
    total_no_chars = complex_words = positive_score = negative_score = 0
    syllable_count_per_word = {}

    for token in text:
        syllable_count = getSyllableCount(token)
        complex_words += 1 if(syllable_count) > 2 else 0
        syllable_count_per_word[token] = syllable_count
        total_no_chars += len(token)

        positive_score += 1 if token in positive_words else 0
        negative_score += -1 if token in negative_words else 0

    negative_score = negative_score * (-1)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)

    subjectivity_score = (positive_score + negative_score) / ((no_of_words) + 0.000001)

    sentiments = {"positive_score": positive_score, 
                "negative_score":negative_score, 
                "polarity_score":polarity_score,
                "subjectivity_score":subjectivity_score,
                "syllable_count_per_word":syllable_count_per_word} 

    return sentiments, total_no_chars, complex_words



def processPipeline():

    files = os.listdir(os.path.join(FILES))

    sentiment_dictionary = {}

    for file in files:
        with open(os.path.join(FILES, file), 'r', encoding='utf8') as f:
            content = f.read()

        cleaned_content, no_of_words = cleanText(content)
        
        # sentiment Analysis and other analytics
        sentiments, total_no_of_chars, complex_words = analytics(cleaned_content, no_of_words)
        
        ids = file.split(".")[0]

        sentiment_dictionary[ids] = sentiments

        average_sentence_length, percentage_of_complex_words, fog_index = readabilityAnalysis(content, 
                                                            no_of_words, complex_words)

        cleaned_content =  " ".join(cleaned_content)
        pronouns_count = personalPronouns(cleaned_content)
        average_word_length = averageWordLength(total_no_of_chars, no_of_words)

        sentiment_dictionary[ids]["average_sentence_length"] = average_sentence_length
        sentiment_dictionary[ids]["percentage_of_complex_words"] = percentage_of_complex_words
        sentiment_dictionary[ids]["fog_index"] = fog_index
        sentiment_dictionary[ids]["average_number_of_words_per_sentence"] = average_sentence_length
        sentiment_dictionary[ids]["complex_word_count"] = complex_words
        sentiment_dictionary[ids]["word_count"] = no_of_words
        sentiment_dictionary[ids]["pronouns_count"] = pronouns_count
        sentiment_dictionary[ids]["average_word_length"] = average_word_length
    
    createFrame(sentiment_dictionary)


def personalPronouns(text):
    
    personal_pronouns = ["I", "we", "We", "my", "My", "ours", "Ours", "us", "Us", "US"]
    matches = re.findall(r"\b(?:{})\b".format("|".join(personal_pronouns)), text)
    counts = {pronoun: matches.count(pronoun) for pronoun in personal_pronouns}
    counts.pop("US", None)

    return counts


def readabilityAnalysis(text, no_of_words, complex_words):

    sentences = nltk.sent_tokenize(text)


    average_sentence_length = no_of_words / len(sentences)
    percentage_of_complex_words = complex_words / no_of_words
    fog_index = 0.4 * (average_sentence_length + percentage_of_complex_words)

    return average_sentence_length, percentage_of_complex_words, fog_index

def getSyllableCount(token):
    syllable_count = syllables.estimate(token)
    token = str(token)
    if token.endswith("es") or token.endswith("ed"):
        syllable_count -= 1

    return syllable_count

def averageWordLength(total_no_of_chars, no_of_words):
    return total_no_of_chars / no_of_words


def createFrame(sentiment_dictionary):

    df_url = pd.read_excel("Input.xlsx")
    df = pd.DataFrame(columns=['URL_ID','URL','POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE' ,
                            'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX', 'AVG NUMBER OF WORDS PER SENTENCE',
                            'COMPLEX WORD COUNT', 'WORD COUNT', 'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH'])
    
    url_count = 0
    for key, data in sentiment_dictionary.items():  

        all_data = [key, str(df_url[df_url["URL_ID"] == int(key)]['URL'].values[0]), data['positive_score'], data['negative_score'], data['polarity_score'],
                            data['subjectivity_score'], data['average_sentence_length'], data['percentage_of_complex_words'],
                            data['fog_index'], data['average_number_of_words_per_sentence'], data['complex_word_count'],data['word_count'], 
                            data['syllable_count_per_word'], data['pronouns_count'], data['average_word_length']]


        df.loc[url_count] = all_data
        url_count += 1

    df.to_csv('Output.csv', index=False)


processPipeline()
