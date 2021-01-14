from pymongo import MongoClient
from tensorflow.keras.preprocessing.text import text_to_word_sequence
import json
import passwords


#page size - number of posts in page, page_num - page number to return
def getposts(page_size, page_num, query, collection):
    
    skips = page_size * (page_num -1)
    cursor = collection.find(query).skip(skips).limit(page_size)

    return [x for x in cursor]


def generateDictionary():

    client = MongoClient(passwords.mongoSRV)
    db = client['quicpos']
    collection = db['posts']

    page_size = 100
    idx = 1
    dictionary = []

    while True:
        
        if idx % 50 == 0:
            print("{}: Downloading posts, ".format(idx), end='')
        posts = getposts(page_size, idx, {}, collection)
        
        if len(posts) == 0:
            break

        for post in posts:
            tokens = text_to_word_sequence(post['text'])

            for token in tokens:
                if token not in dictionary:
                    dictionary.append(token)

        if idx % 50 == 0:
            print("dictionary len: {}".format(len(dictionary)))
        idx += 1

    print("Final dictionary len: {}".format(len(dictionary)))

    with open('dictionary.json', 'w') as f:
        json.dump(dictionary, f)
