import requests
import json
import sys
import time
from os import listdir
from os.path import isfile, join

bearer = "Bearer AAAAAAAAAAAAAAAAAAAAAFJmJAEAAAAAiKXgs71WHr8Ay76lBSPzZfDBIOo%3DZH4yblNSZC1J4YUNIrLpW8mWaeZRDtUQDUrm83NLmuQM1wmxnq"
params = {"tweet.fields": "created_at,public_metrics,entities", "expansions": "attachments.media_keys", "media.fields": "url", "end_time": "2020-10-24T00:00:00+00:00", "max_results": "30"}
keywords = []
numtweets = 0

#already downloaded tweets
files = [f for f in listdir("data/") if isfile(join("data/", f))]
for file in files:
    with open("data/" + file, "r") as read_file:
        data = json.load(read_file)
        try:
            numtweets += len(data['data'])
        except KeyError:
            print("INFO: No tweets for {} keyword".format(file))


#addition in case of faliure or pause
addition = 1340
counter = [time.time()] * addition

#clean array with 15min 10s = 910s interval
def cleanCounter():
    global counter
    now = time.time()
    temp = []
    for count in counter:
        if now - count < 910:
            temp.append(count)
    counter = temp

#read keywords
with open("keywords.txt", "r") as read_file:
    data = read_file.read()
    keywords = data.split(',')

#450 requests in 15 min
#app auth - tweets not personalized
#user auth - tweets show as logged in user

#get tweets
for idx, keyword in enumerate(keywords[addition:]):

    keyword = keyword.replace('/', '')
    keyword = keyword.replace(':', '')
    keyword = keyword.replace('&', '')
    keyword = keyword.replace("'", '')
    cleanCounter()
    #rate limits watch
    while len(counter) >= 449:
        print("INFO: Waiting to not overpass rate limits...")
        time.sleep(60)
        cleanCounter()

    #download
    print("\nPROGRESS: {:.1f}%, keyword: {}, idx: {}".format((idx+addition)*100/len(keywords), keyword, idx + addition))
    resp = requests.get('https://api.twitter.com/2/tweets/search/recent?query=' + keyword, headers={"Authorization":bearer}, params=params)
    counter.append(time.time())

    #save
    if resp.status_code != 200:
        print("INFO: Can't get tweets")
    else:
        with open('data/' + keyword + '.json', 'w') as outfile:
            data = resp.json()
            try:
                numtweets += len(data['data'])
            except KeyError:
                print("INFO: No tweets for {} keyword".format(keyword))
            json.dump(resp.json(), outfile)

print("Number of tweets in data folder: {}".format(numtweets))