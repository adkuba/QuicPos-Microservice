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

#Init trainer
client = MongoClient("mongodb+srv://admin:funia@quicpos.felpr.gcp.mongodb.net/quicpos?retryWrites=true&w=majority")
db = client['quicpos']
collection = db['posts']

shutil.rmtree('./training', ignore_errors=True)

#page size - number of posts in page
#page_num - page number to return
def getposts(page_size, page_num):
    
    skips = page_size * (page_num -1)
    cursor = collection.find({"blocked": False}).skip(skips).limit(page_size)

    return [x for x in cursor]

def share(array, uid):
    if array:
        if uid in array:
            return 1
    return 0


#Create training set for recommender
os.mkdir('./training')
os.mkdir('./training/recommender')
os.mkdir('./training/recommender/train')
os.mkdir('./training/recommender/test')

#process posts in batches of 100
size = 100
idx = 1
users = []

while True:
    posts = getposts(size, idx)
    idx += 1
    post_data = []
    for post in posts:
        views = post['views']
        if views:
            #prepare values
            del post['_id']
            post['creationtime'] = int(datetime.timestamp(post['creationtime']))
            temp = []
            for view in views:
                view['date'] = int(datetime.timestamp(view['date']))
                del view['localization']
                temp.append(view)
            views = temp
            if post['shares'] == None:
                post['shares'] = []
            if post['reports'] == None:
                post['reports'] = []
            del post['blocked']
            del post['initialreview']
            text = []
            for idx in range(400):
                ch = 0
                if idx < len(post['text']):
                    ch = ord(post['text'][idx])
                text.append(ch)
            post['text'] = text
            #image = [[[ [0]*3 ]*224 ]*224]
            #if post['image'] != "":
                #response = requests.get("https://storage.googleapis.com/quicpos-images/" + post['image'] + "_small")
                #if response.status_code == 200:
                    #imagePIL = Image.open(io.BytesIO(response.content))
                    #imagePIL.show()
                    #image = numpy.array(imagePIL).tolist()
            #post['image'] = image


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

                data['time'] = view['time']
                data['share'] = share(post['shares'], view['userid'])
                
                post_data.append(data)
                
            #json_data = json.dumps(post_data)
            #print(json_data)
            with open('./training/test.json', 'w') as outfile:
                json.dump(post_data, outfile)
            sys.exit(0)


#views = posts[0]['views']
#day = posts[0]['creationtime']
#print(day)
