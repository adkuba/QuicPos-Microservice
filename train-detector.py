from pymongo import MongoClient
from datetime import datetime
from tensorflow.keras.preprocessing.text import text_to_word_sequence
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
import json
import time
import scp_sender
import pickle


#Init trainer
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
client = MongoClient("mongodb+srv://admin:ayeM3cKxV0AR4136@quicpos.felpr.gcp.mongodb.net/quicpos?retryWrites=true&w=majority")
db = client['quicpos']
collection = db['posts']
dictionary = []


with open('dictionary.json', 'r') as fp:
    dictionary = json.load(fp)


#page size - number of posts in page, page_num - page number to return
def getposts(page_size, page_num, query):
    
    skips = page_size * (page_num -1)
    cursor = collection.find(query).skip(skips).limit(page_size)

    return [x for x in cursor]


#difference of two lists
def diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


#prepare post
def dataPrepare(post):
    del post['_id']
    del post['reports']
    del post['views']
    del post['shares']
    del post['creationtime']
    del post['initialreview']
    del post['blocked']
    del post['money']
    del post['outsideviews']
    del post['image']
    del post['user']

    return post


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


#blocked to number
def isSpam(blocked):
    if blocked:
        return 1
    return 0


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

    #print(image)
    return text, image



#detector generator
def detectorGenerator(path):
    while True:
        atext = []
        aimage = []
        aoutSpam = []

        for file in os.listdir(path):
            with open(path + "/" + file) as infile:
                data_set = json.load(infile)
                for data in data_set:
                    #post data
                    text, image = postGenData(data['post'])
                    aimage.append(image)
                    atext.append(text)

                    #out spam
                    aoutSpam.append([data['spam']])

                    if len(aoutSpam) == batch_size:
                        yield [numpy.array(atext), numpy.array(aimage)], numpy.array(aoutSpam)
                        atext = []
                        aimage = []
                        aoutSpam = []



#Create training set for recommender
shutil.rmtree('./training', ignore_errors=True)
os.mkdir('./training')
os.mkdir('./training/detector')
os.mkdir('./training/detector/train')
os.mkdir('./training/detector/test')


#process posts in batches of 100
size = 100
idx = 1
detector_train_size = 0
detector_test_size = 0


#spam posts data
while True:
    post_data = []
    posts_blocked = getposts(int(size/2), idx, {"blocked": True, "humanreview": True, "initialreview": True})
    posts_ok = getposts(int(size/2), idx, {"blocked": False, "humanreview": True, "initialreview": True})
    if len(posts_blocked) == 0 or len(posts_ok) == 0:
        break

    posts = posts_blocked + posts_ok

    for post in posts:
        data = {}
        data['spam'] = isSpam(post['blocked'])
        post = dataPrepare(post)
        data['post'] = post
        post_data.append(data)

    a, b = saver(post_data, './training/detector')
    detector_train_size += a
    detector_test_size += b
    idx += 1


batch_size = 32


#train detector
detector_train_gen = detectorGenerator("./training/detector/train")
detector_test_gen = detectorGenerator("./training/detector/test")
epochs = 100
steps_per_epoch = detector_train_size / batch_size
validation_steps = detector_test_size / batch_size

model = keras.models.load_model("./out/detector_new_init.h5")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="./logs")
history = model.fit(detector_train_gen, validation_data=detector_test_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, validation_steps=validation_steps, callbacks=[tensorboard_callback])

detector_acc = history.history['val_accuracy'][-1]
print()
print("DETECTOR ACCURACY: " + str(history.history['val_accuracy'][-1]))
print()

with open("./training/detector_history", 'wb') as filepi:
    pickle.dump(history.history, filepi)

model.save("./out/detector_new.h5")
tf.saved_model.save(model, "./out/detector")