from pymongo import MongoClient
from tensorflow.keras.preprocessing.text import text_to_word_sequence
import pickle

#Init
client = MongoClient("mongodb+srv://admin:ayeM3cKxV0AR4136@quicpos.felpr.gcp.mongodb.net/quicpos?retryWrites=true&w=majority")
db = client['quicpos']
collection = db['posts']


#page size - number of posts in page, page_num - page number to return
def getposts(page_size, page_num, query):
    
    skips = page_size * (page_num -1)
    cursor = collection.find(query).skip(skips).limit(page_size)

    return [x for x in cursor]


page_size = 100
idx = 1
dictionary = []

while True:
    
    print("{}: Downloading posts, ".format(idx), end='')
    posts = getposts(page_size, idx, {})
    
    if len(posts) == 0:
        break

    for post in posts:
        tokens = text_to_word_sequence(post['text'])

        for token in tokens:
            if token not in dictionary:
                dictionary.append(token)

    print("dictionary len: {}".format(len(dictionary)))
    idx += 1


with open('dictionary', 'wb') as f:
    pickle.dump(dictionary, f)
