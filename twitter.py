import requests
import json
import sys

bearer = "Bearer AAAAAAAAAAAAAAAAAAAAAFJmJAEAAAAAiKXgs71WHr8Ay76lBSPzZfDBIOo%3DZH4yblNSZC1J4YUNIrLpW8mWaeZRDtUQDUrm83NLmuQM1wmxnq"
params = {"tweet.fields": "created_at,public_metrics,entities", "expansions": "attachments.media_keys", "media.fields": "url", "end_time": "2020-10-22T00:00:00+00:00"}

#get tweets
resp = requests.get('https://api.twitter.com/2/tweets/search/recent?query=python', headers={"Authorization":bearer}, params=params)

# This means something went wrong.
if resp.status_code != 200:
    print('GET /tasks/ {}'.format(resp.status_code))
    sys.exit(1)

#save
with open('data.json', 'w') as outfile:
    json.dump(resp.json(), outfile)