import json
import base64
import requests

tweets = []
media = []
ids = []

def findUrl(mediaKey):
    for mediaObject in media:
        if mediaObject['media_key'] == mediaKey:
            if mediaObject['type'] == 'photo':
                return mediaObject['url']
            return 'not-photo'

with open("data/data.json", "r") as read_file:
    data = json.load(read_file)
    tweets = data['data']
    media = data['includes']['media']

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
                
            try:    
                hashtags = entities['hashtags']
                for hashtag in hashtags:
                    start = hashtag['start']
                    textStart = text[:start-textOffset]
                    textEnd = text[start+1-textOffset:]
                    textOffset += 1
                    text = textStart + textEnd
            except KeyError:
                print("INFO: No hashtags!")
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
                            photo = base64.b64encode(response.content)
                            urlArray = url.split('.')
                            photo = "data:image/" + urlArray[-1] + ";base64,"
                            break
            except KeyError:
                print("INFO: No media keys!")
        except KeyError:
            print("INFO: No attachments!")

        text = text.replace("RT : ", "")
        text = text.strip()
        print("text: {}\nphoto: {}\n".format(text, photo))