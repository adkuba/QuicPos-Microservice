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


#Init trainer
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
client = MongoClient("mongodb+srv://admin:funia@quicpos.felpr.gcp.mongodb.net/quicpos?retryWrites=true&w=majority")
db = client['quicpos']
collection = db['posts']


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
    del post['blocked']
    del post['initialreview']
    del post['outsideviews']
    post['creationtime'] = float(datetime.timestamp(post['creationtime']))/100000.0
    temp = []
    if views:
        for view in views:
            view['date'] = float(datetime.timestamp(view['date']))/100000.0
            del view['localization']
            temp.append(view)
    views = temp
    if post['shares'] == None:
        post['shares'] = []
    if post['reports'] == None:
        post['reports'] = []
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


#blocked to number
def isSpam(blocked):
    if blocked:
        return 1
    return 0


#post generator data
def postGenData(post):
    #text
    text = []
    for idx in range(400):
        ch = 0
        if idx < len(post['text']):
            ch = ord(post['text'][idx])
        text.append(ch)
    
    #user
    user = [post['userid']]

    #reports
    reports = []
    for idx in range(100):
        report = 0
        if idx < len(post['reports']):
            report = post['reports'][idx]
        reports.append(report)
    random.shuffle(reports)

    #creation
    creation = [post['creationtime']]

    #image
    image = [[ [0]*3 ]*224 ]*224
    if post['image'] != "":
        try:
            response = requests.get("https://storage.googleapis.com/quicpos-images/" + post['image'] + "_small")
            if response.status_code == 200:
                imagePIL = Image.open(io.BytesIO(response.content))
                imagePIL = imagePIL.convert('RGB')
                imageNumpy = numpy.array(imagePIL)
                image = imageNumpy.tolist()
        except:
            print("CANT download image")

    #views
    views = []
    for idx in range(100):
        view = [0] * 6
        if idx < len(post['views']):
            userView = post['views'][idx]['userid']
            deviceView = post['views'][idx]['device']
            latiView = post['views'][idx]['lati']
            longView = post['views'][idx]['long']
            timeView = post['views'][idx]['time']
            dateView = post['views'][idx]['date']
            view = [userView, deviceView, latiView, longView, timeView, dateView]
        views.append(view)
    random.shuffle(views)

    #shares
    shares = []
    for idx in range(100):
        share = 0
        if idx < len(post['shares']):
            share = post['shares'][idx]
        shares.append(share)
    random.shuffle(shares)

    return text, user, reports, creation, image, views, shares


#recomennder data generator
def recommenderGenerator(path):
    while True:
        atext = []
        auser = []
        areports = []
        acreation = []
        aimage = []
        aviews = []
        ashares = []
        arequestingUser = []
        arequestingLati = []
        arequestingLong = []
        arequestingTime = []
        aOut = []

        for file in os.listdir(path):
            with open(path + "/" + file) as infile:
                data_set = json.load(infile)
                for data in data_set:
                    #post data
                    text, user, reports, creation, image, views, shares = postGenData(data['post'])
                    ashares.append(shares)
                    aviews.append(views)
                    aimage.append(image)
                    acreation.append(creation)
                    areports.append(reports)
                    auser.append(user)
                    atext.append(text)

                    #requesting user
                    requestingUser = data['userid']
                    arequestingUser.append(requestingUser)

                    #requesting lati
                    requestingLati = data['lati']
                    arequestingLati.append(requestingLati)

                    #requesting long
                    requestingLong = data['long']
                    arequestingLong.append(requestingLong)

                    #requesting time
                    requestingTime = data['requesttime']
                    arequestingTime.append(requestingTime)

                    #out
                    aOut.append(data['time'])

                    if len(aOut) == batch_size:
                        yield [numpy.array(atext), numpy.array(auser), numpy.array(areports), numpy.array(acreation), numpy.array(aimage), numpy.array(aviews), numpy.array(ashares), numpy.array(arequestingUser), numpy.array(arequestingLati), numpy.array(arequestingLong), numpy.array(arequestingTime)], numpy.array(aOut)
                        atext = []
                        auser = []
                        areports = []
                        acreation = []
                        aimage = []
                        aviews = []
                        ashares = []
                        arequestingUser = []
                        arequestingLati = []
                        arequestingLong = []
                        arequestingTime = []
                        aOut = []


#detector generator
def detectorGenerator(path):
    while True:
        atext = []
        auser = []
        areports = []
        acreation = []
        aimage = []
        aviews = []
        ashares = []
        aoutSpam = []

        for file in os.listdir(path):
            with open(path + "/" + file) as infile:
                data_set = json.load(infile)
                for data in data_set:
                    #post data
                    text, user, reports, creation, image, views, shares = postGenData(data['post'])
                    ashares.append(shares)
                    aviews.append(views)
                    aimage.append(image)
                    acreation.append(creation)
                    areports.append(reports)
                    auser.append(user)
                    atext.append(text)

                    #out spam
                    aoutSpam.append([data['spam']])

                    if len(aoutSpam) == batch_size:
                        yield [numpy.array(atext), numpy.array(auser), numpy.array(areports), numpy.array(acreation), numpy.array(aimage), numpy.array(aviews), numpy.array(ashares)], numpy.array(aoutSpam)
                        atext = []
                        auser = []
                        areports = []
                        acreation = []
                        aimage = []
                        aviews = []
                        ashares = []
                        aoutSpam = []


while True:
    #Create training set for recommender
    shutil.rmtree('./training', ignore_errors=True)
    os.mkdir('./training')
    os.mkdir('./training/recommender')
    os.mkdir('./training/recommender/train')
    os.mkdir('./training/recommender/test')
    os.mkdir('./training/detector')
    os.mkdir('./training/detector/train')
    os.mkdir('./training/detector/test')


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
                data['userid'] = view['userid']
                data['long'] = view['long']
                data['lati'] = view['lati']
                data['requesttime'] = view['date']

                viewsClone = views.copy()
                viewsClone.remove(view)
                postClone = post.copy()
                postClone['views'] = viewsClone
                data['post'] = postClone

                #very bad post
                if view['time'] <= 2:
                    data['time'] = [1, 0, 0, 0, 0]
                #bad post
                elif view['time'] > 2 and view['time'] <= 4:
                    data['time'] = [0, 1, 0, 0, 0]
                #avarage post
                elif view['time'] > 4 and view['time'] <= 7:
                    data['time'] = [0, 0, 1, 0, 0]
                #good post
                elif view['time'] > 7 and view['time'] <= 15:
                    data['time'] = [0, 0, 0, 1, 0]
                #amazing post
                else:
                    data['time'] = [0, 0, 0, 0, 1]
                post_data.append(data)
        
        a, b = saver(post_data, './training/recommender')
        recommender_train_size += a
        recommender_test_size += b
        idx += 1


    idx = 1
    detector_train_size = 0
    detector_test_size = 0


    #spam posts data
    while True:
        post_data = []
        posts = getposts(size, idx, {})
        if len(posts) == 0:
            break

        for post in posts:
            data = {}
            data['spam'] = isSpam(post['blocked'])
            post, views = dataPrepare(post, post['views'])
            post['views'] = views
            data['post'] = post
            post_data.append(data)

        a, b = saver(post_data, './training/detector')
        detector_train_size += a
        detector_test_size += b
        idx += 1


    batch_size = 32


    #train recommender
    recommender_train_gen = recommenderGenerator("./training/recommender/train")
    recommender_test_gen = recommenderGenerator("./training/recommender/test")
    epochs = 20
    steps_per_epoch = recommender_train_size / batch_size
    validation_steps = recommender_test_size / batch_size

    model = keras.models.load_model("./out/recommender.h5")
    history = model.fit(recommender_train_gen, validation_data=recommender_test_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, validation_steps=validation_steps)

    recommender_acc = history.history['val_accuracy'][-1]
    print()
    print("RECOMMENDER ACCURACY: " + str(history.history['val_accuracy'][-1]))
    print()

    with open("./training/recommender_history", 'wb') as filepi:
        pickle.dump(history.history, filepi)

    model.save("./out/recommender.h5")
    tf.saved_model.save(model, "./out/recommender")


    #train detector
    detector_train_gen = detectorGenerator("./training/detector/train")
    detector_test_gen = detectorGenerator("./training/detector/test")
    epochs = 5
    steps_per_epoch = detector_train_size / batch_size
    validation_steps = detector_test_size / batch_size

    model = keras.models.load_model("./out/detector.h5")
    history = model.fit(detector_train_gen, validation_data=detector_test_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, validation_steps=validation_steps)

    detector_acc = history.history['val_accuracy'][-1]
    print()
    print("DETECTOR ACCURACY: " + str(history.history['val_accuracy'][-1]))
    print()

    with open("./training/detector_history", 'wb') as filepi:
        pickle.dump(history.history, filepi)

    model.save("./out/detector.h5")
    tf.saved_model.save(model, "./out/detector")


    query = """mutation learning {
        learning(input: { recommender: %f, detector: %f }, password: "%s")   
    }""" % (recommender_acc, detector_acc, "kuba")

    r = requests.post("https://www.api.quicpos.com/query", json={'query': query}, verify=False)
    print("SENDING: " + str(r.status_code))

    #wait 1 day
    time.sleep(60 * 60 * 24)
