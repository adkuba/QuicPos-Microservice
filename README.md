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



## Neural net
Neural nets description.

### Recommender net
Recommender neural net in/out:
* input: 5 last posts, posts to compare -> TEST HOW FAST NET WORKS! and change number of last posts. In addition userID of request! 6x array of object:
    - text - string
    - userID - string
    - reports - array of userID - string
    - creationTime - date
    - image 224x224 rgb
    - views - array object {userID - string, time - float, localization - string, device - string, date - date}
    - shares - array of userID - string
* output: time, share
    - float and bool

### Spam detector
Spam detector neural net in/out:
* input: post to review
    - text - string
    - userID - string
    - reports - array of userID - string
    - creationTime - date
    - image 224x224 rgb
    - views - array object {userID - string, time - float, localization - string, device - string, date - date}
    - shares - array of userID - string
* output: spam or not
    - bool

### Structure
* Image connected to mobile net similar structure
* Hidden units 256
* Hidden layers init 2 - TEST SPEED and change number of layers!

### How to create fixed size input ???
Hash from object?
