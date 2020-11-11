import json
import base64
import requests
from os import listdir
from os.path import isfile, join
import sys


ids = []
url = "http://localhost:8080/query"
files = [f for f in listdir("data/") if isfile(join("data/", f))]
addition = 4191


def findUrl(mediaKey):
    for mediaObject in media:
        if mediaObject['media_key'] == mediaKey:
            if mediaObject['type'] == 'photo':
                return mediaObject['url']
            return 'not-photo'


for idx, file in enumerate(files[addition:]):

    print("\nPROCESSING: {:.1f}%, tweets for keyword: {}, idx {}".format((idx+addition)*100/len(files), file, idx+addition))
    tweets = []
    media = []
    if file == ".gitkeep":
        continue

    with open("data/" + file, "r") as read_file:
        data = json.load(read_file)
        try:
            tweets = data['data']
        except KeyError:
            print("INFO: No tweets for {} keyword".format(file))
        try:
            media = data['includes']['media']
        except KeyError:
            print("INFO: No tweets media for {} keyword".format(file))

    for tweet in tweets:
        tweetID = tweet['id']
        print("INFO: Processing {:.1f}%, tweet: {}".format((idx+addition)*100/len(files), tweetID))

        #check if tweet is not duplicate
        if tweetID not in ids:
            ids.append(tweetID)
            
            text = tweet['text']
            photo = ""
            textOffset = 0
            
            #parse text
            text = text.replace("#", "")
            text = text.replace("@", "")
            text = text.replace('\n', '\\n')
            text = text.replace('"', "'")

            skip = False

            #search for image
            try:
                attachments = tweet['attachments']
                try:
                    mediaKeys = attachments['media_keys']
                    for key in mediaKeys:
                        urlIMG = findUrl(key)
                        if urlIMG != 'not-photo':
                            response = requests.get(urlIMG)
                            if response.status_code != 200:
                                print("INFO: Can't get photo for tweet {}".format(tweetID))
                            else:
                                photo = str(base64.b64encode(response.content))
                                urlArray = urlIMG.split('.')
                                if urlArray[-1] not in ['jpg', 'jpeg']:
                                    skip = True
                                photo = "data:image/" + urlArray[-1] + ";base64," + photo[2:len(photo)-1]
                                break
                except KeyError:
                    print("INFO: No media keys!")
            except KeyError:
                print("INFO: No attachments!")

            if skip:
                print("SKIPPING: Not jpeg")
                continue

            text = text.replace("RT ", "")
            text = text.strip()

            query = """mutation create {
                createPost(
                    input: {
                    text: "%s"
                    userId: %i
                    image: "%s"
                    }
                ) {
                    ID
                    text
                    userId
                    shares
                    views
                    creationTime
                    initialReview
                    image
                }
            }""" % (text, -2, photo)

            r = requests.post(url, json={'query': query})
            print("SENDING: " + str(r.status_code))

            if r.status_code != 200:
                print(query)
            
            print()