from pymongo import MongoClient
from datetime import datetime
import shutil
import os
import json
import sys
import requests
from PIL import Image
import io
import numpy
import random
from tensorflow import keras
import tensorflow as tf
import pickle
import time
import scp_sender
from keras_preprocessing.text import text_to_word_sequence
import passwords
import dictionary as dc


#Init trainer
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
client = MongoClient(passwords.mongoSRV)
db = client['quicpos']
collection = db['posts']
dictionary = []


#page size - number of posts in page, page_num - page number to return
def getposts(page_size, page_num, query):
    
    skips = page_size * (page_num -1)
    cursor = collection.find(query).skip(skips).limit(page_size)

    return [x for x in cursor]


#difference of two lists
def diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


#prepare post and views
def dataPrepare(post, views):
    del post['_id']
    del post['reports']
    del post['creationtime']
    del post['image']
    del post['initialreview']
    del post['blocked']
    del post['money']
    del post['outsideviews']
    del post['humanreview']

    #views
    temp = []
    if views:
        for view in views:
            del view['localization']
            del view['ip']
            del view['device']
            del view['date']
            temp.append(view)
    views = temp

    #shares
    if post['shares'] != None:
        post['shares'] = len(post['shares'])
    else:
        post['shares'] = 0

    return post, views


#save posts 20% to test 80% to train
def saver(posts, path):
    post_test = []
    for _ in range(int(len(post_data)*0.2)):
        post_test.append(random.choice(posts))
    post_train = diff(post_data, post_test)

    #save
    with open(path + '/test/' + str(idx) + '.json', 'w') as outfile:
        json.dump(post_test, outfile)
    with open(path + '/train/' + str(idx) + '.json', 'w') as outfile:
        json.dump(post_train, outfile)

    return len(post_train), len(post_test)


#post generator data
def postGenData(post):
    #text
    tokens = text_to_word_sequence(post['text'])
    text = [ dictionary.index(token) for token in tokens ]

    if len(text) > 200:
        text = text[0:200]
    else:
        for _ in range(200-len(text)):
            text.append(-1)

    #print(text)

    #image
    image = [0] * 1280
    if post['imagefeatures'] != None:
        image = post['imagefeatures']

    return text, image, len(post['views']), post['shares']


def medianFile(path):
    temp = []
    for file in os.listdir(path):
            with open(path + "/" + file) as infile:
                data_set = json.load(infile)
                for data in data_set:
                    temp.append(float(data['time']))
    return temp

def getMedian():
    allTimes = []
    allTimes += medianFile('./training/recommender/train')
    allTimes += medianFile('./training/recommender/test')
    allTimes.sort()
    return allTimes[int(len(allTimes)/2)]


#recomennder data generator
def recommenderGenerator(path):
    while True:
        atext = []
        aimage = []
        auser = []
        aviews = []
        ashares = []
        aOut = []

        for file in os.listdir(path):
            with open(path + "/" + file) as infile:
                data_set = json.load(infile)
                for data in data_set:
                    #post data
                    text, image, views, shares = postGenData(data['post'])
                    ashares.append(shares)
                    aviews.append(views)
                    aimage.append(image)
                    atext.append(text)

                    #requesting user
                    bytesUser = bytearray.fromhex(data['userid'])
                    user = []
                    user.append(numpy.uint32(int.from_bytes(bytesUser[0:4], 'big')))
                    user.append(numpy.uint32(int.from_bytes(bytesUser[4:8], 'big')))
                    user.append(numpy.uint32(int.from_bytes(bytesUser[8:12], 'big')))
                    user.append(numpy.uint32(int.from_bytes(bytesUser[12:16], 'big')))
                    auser.append(user)

                    #out
                    if data['time'] > median:
                        aOut.append(1)
                    else:
                        aOut.append(0)

                    #print(auser)

                    if len(aOut) == batch_size:
                        yield [numpy.array(atext), numpy.array(aimage), numpy.array(auser), numpy.array(aviews), numpy.array(ashares)], numpy.array(aOut)
                        atext = []
                        aimage = []
                        auser = []
                        aviews = []
                        ashares = []
                        aOut = []



while True:

    dc.generateDictionary()

    with open('dictionary.json', 'r') as fp:
        dictionary = json.load(fp)

    #Create training set for recommender
    shutil.rmtree('./training', ignore_errors=True)
    os.mkdir('./training')
    os.mkdir('./training/recommender')
    os.mkdir('./training/recommender/train')
    os.mkdir('./training/recommender/test')


    #process posts in batches of 100
    size = 100
    idx = 1
    recommender_train_size = 0
    recommender_test_size = 0

    #Rocommender data
    while True:
        post_data = []
        posts = getposts(size, idx, {"blocked": False, "views": {"$ne": None}})
        if len(posts) == 0:
            break
        
        for post in posts:
            #prepare values
            post, views = dataPrepare(post, post['views'])

            #create training set for every user
            for view in views:
                data = {}
                data['userid'] = view['user']

                postClone = post.copy()
                data['post'] = postClone
                data['time'] = view['time']
                
                post_data.append(data)
        
        #print(post_data)
        a, b = saver(post_data, './training/recommender')
        recommender_train_size += a
        recommender_test_size += b
        idx += 1


    batch_size = 8


    median = 3
    median = getMedian()
    print()
    print("Median time: {}".format(median))
    print()
    #train recommender
    recommender_train_gen = recommenderGenerator("./training/recommender/train")
    recommender_test_gen = recommenderGenerator("./training/recommender/test")
    epochs = 100
    steps_per_epoch = recommender_train_size / batch_size
    validation_steps = recommender_test_size / batch_size

    model = keras.models.load_model("./out/recommender_init.h5")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="./logs")
    history = model.fit(recommender_train_gen, validation_data=recommender_test_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, validation_steps=validation_steps, callbacks=[tensorboard_callback])

    recommender_acc = history.history['val_accuracy'][-1]
    print()
    print("RECOMMENDER ACCURACY: " + str(history.history['val_accuracy'][-1]))
    print()

    with open("./training/recommender_history", 'wb') as filepi:
        pickle.dump(history.history, filepi)

    model.save("./out/recommender.h5")
    tf.saved_model.save(model, "./out/recommender")

    #scp send
    scp_sender.sendRecommender()

    #update files
    query = """mutation learning {
        learning(input: { recommender: %f, detector: %f }, password: "%s")   
    }""" % (recommender_acc, -1, passwords.password)

    r = requests.post("https://www.api.quicpos.com/query", json={'query': query})
    print()
    print("SENDING: " + str(r.status_code))
    print()

    #wait 6 hours
    time.sleep(60)