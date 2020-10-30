import json
import base64
import requests
from os import listdir
from os.path import isfile, join


ids = []
url = "http://www.api.quicpos.com/query"
files = [f for f in listdir("data/") if isfile(join("data/", f))]



def findUrl(mediaKey):
    for mediaObject in media:
        if mediaObject['media_key'] == mediaKey:
            if mediaObject['type'] == 'photo':
                return mediaObject['url']
            return 'not-photo'


for idx, file in enumerate(files):

    print("\nPROCESSING: {:.1f}%, tweets for keyword: {}".format(idx*100/len(files), file))
    tweets = []
    media = []

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
        print("INFO: Processing {}".format(tweetID))

        #check if tweet is not duplicate
        if tweetID not in ids:
            ids.append(tweetID)
            
            text = tweet['text']
            photo = ""
            textOffset = 0
            
            #parse text
            text = text.replace("#", "")
            try:
                entities = tweet['entities']
                try:
                    mentions = entities['mentions']
                    for mention in mentions:
                        start = mention['start']
                        end = mention['end']
                        textStart = text[:start-textOffset]
                        textEnd = text[end-textOffset:]
                        textOffset += end - start
                        text = textStart + textEnd
                except KeyError:
                    print("INFO: No mentions!")
            except KeyError:
                print("INFO: No entities!")


            #search for image
            try:
                attachments = tweet['attachments']
                try:
                    mediaKeys = attachments['media_keys']
                    for key in mediaKeys:
                        url = findUrl(key)
                        if url != 'not-photo':
                            response = requests.get(url)
                            if response.status_code != 200:
                                print("INFO: Can't get photo for tweet {}".format(tweetID))
                            else:
                                photo = str(base64.b64encode(response.content))
                                urlArray = url.split('.')
                                photo = "data:image/" + urlArray[-1] + ";base64," + photo[2:len(photo)-1]
                                break
                except KeyError:
                    print("INFO: No media keys!")
            except KeyError:
                print("INFO: No attachments!")

            text = text.replace("RT : ", "")
            text = text.strip()

            query = """mutation create {
                createPost(
                    input: {
                    text: "%s"
                    userId: "%s"
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
            }""" % (text, "bot", photo)

            r = requests.post(url, json={'query': query})
            print("SENDING: " + r.status_code + "\n")