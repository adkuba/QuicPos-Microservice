# QuicPos-Microservice
Machine learning workflow, python microservice.

## Twitter bot files
All with progress info and reusability in mind.

### trends.py
Gets from Google Trends keywords to search tweets later.
* Top searches for selected year and country
* Today trending for selected country
* Related keywords for above categories

### twitter.py
Data fetch from twitter - initial data for my service. I need to have pure text with links and image.
* Warning, end-time works max 1 week back, good value - 1/2 week back or full because there may not be many tweets in selected topic
* Example out in data.json
* Links [doc](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent)
* Bot waits to not overpass rate limits and handles crash/pause

### saver.py
Saves json tweets in data folder to my server.
* text parsing - remove hashtags annotations
* photo find and convert to base64
* check how much space is used in cloud storage <code>gsutil du -sh gs://quicpos-images/</code>
* last idx: 1621



## Neural net
Neural nets description. Important notes about **Text preprocessing for neural net** [notes](https://github.com/adkuba/QuicPos-Server/issues/4#issuecomment-720122145)

### generate-recommender.py
Recommender neural net in/out:
* input: post to compare -> TEST HOW FAST NET WORKS! In addition userID of request! Input:
    - text - 100x array of ints - string converted to int tokens with example keras one hot in golang!
    - userID - uint32 (CHANGE in server from uuid and in mongo collection with last int! max int is 4294967295)
    - reports - array of userID - uint32 100 random chosen ids
    - creationTime - int64 timestamp
    - image 224x224x3 - float input
    - views - 100x array with array {userID - uint32, time - float, latitude - float, longitude - float, device - int, date - int64} (CHANGE in server - add long/lattitude and device to  example 1 - ios 2 - android then 5 digits of phone model, maybe new collection in mongo needed?)
    - shares - 100x array of userID - uint32
    - requesting userID - uint32
    - requesting lat and long-itutte
    - requesting time
* output: time, share
    - float and bool

### generate-detector.py
Spam detector neural net in/out:
* input: similar to recommender, without "requesting *"
* output: spam or not
    - bool

### Structure desc
* flatten arrays!
* for image 2x Conv2D layer to flatten input
* every input has additional dense 128 layer example views params connects to special dense layer. Then 1 dense 256 layer combining all inputs (from 128 dense layers or direct inputs) and final layer is size 2 - recomender system or size 1 spam detector. Combined input for one 128 dense layer:
    - requesting params
    - userID
    - creation time