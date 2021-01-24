# Table of Contents
- [What I've learned](#what-ive-learned)
- [Important](#important)
- [Twitter](#twitter)
    - [Query](#query)
    - [API](#api)
    - [Saving](#saving)
- [Machine learning](#machine-learning)
    - [Structure](#structure)
    - [Training](#training)
    - [Other](#other)



# What I've learned
- Data science in **Python**
- Working with **Twitter API** and **MongoDB**
- How to design and create ML model in **Tensorflow**



# Important
- To open database in mongo shell, type: <code>mongo "mongodb+srv://quicpos.felpr.gcp.mongodb.net/quicpos" --username admin</code>
- Create <code>passwords.py</code> file with Mongo SRV, general password and SSH server password



# Twitter
Napisać jak wyodrębniłem dane z Twittera

### Query
Using [trends.py](trends.py)
Gets from Google Trends keywords to search tweets later.
* Top searches for selected year and country
* Today trending for selected country
* Related keywords for above categories
Wykorzystam recent search - pobiera pasujące do query posty z ostatniego tygodnia.
Query to będą trending hasła z google trends.

Przykładowe zapytanie: 
curl -X GET -H "Authorization: Bearer AAAAAAAAAAAAAAAAAAAAAFJmJAEAAAAAiKXgs71WHr8Ay76lBSPzZfDBIOo%3DZH4yblNSZC1J4YUNIrLpW8mWaeZRDtUQDUrm83NLmuQM1wmxnq" "https://api.twitter.com/2/tweets/20"
OLD keys - new saved on my computer.


### API
Using twitter.py
Data fetch from twitter - initial data for my service. I need to have pure text with links and image.
* Warning, end-time works max 1 week back, good value - 1/2 week back or full because there may not be many tweets in selected topic
* Example out in data.json
* Links [doc](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent)
* Bot waits to not overpass rate limits and handles crash/pause

### Saving
Using saver.py
Saves json tweets in data folder to my server.
* text parsing - remove hashtags annotations
* photo find and convert to base64
* check how much space is used in cloud storage <code>gsutil du -sh gs://quicpos-images/</code>



# Machine learning
Jak powstała sieć neuronowa
Neural nets description. Important notes about **Text preprocessing for neural net** [notes](https://github.com/adkuba/QuicPos-Server/issues/4#issuecomment-720122145)

### Structure
Using generate-recommender.py
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
* output: view category
    - very_bad_view, bad_view, avarage_view, good_view, excellent_view

Using generate-detector.py
Spam detector neural net in/out:
* input: similar to recommender, without "requesting *"
* output: spam or not
    - bool

Structure
* flatten arrays!
* for image 2x Conv2D layer to flatten input
* every input has additional dense 128 layer example views params connects to special dense layer. Then 1 dense 256 layer combining all inputs (from 128 dense layers or direct inputs) and final layer is size 2 - recomender system or size 1 spam detector. Combined input for one 128 dense layer:
    - requesting params
    - userID
    - creation time

### Training
Using train-detector.py train-recommender.py
Prepares data from database and trains nets. Loads data from file, converts image and sends to keras trainer.
- all logs to file <code>SomeCommand &>> SomeFile.txt  </code>

Using dictionary.py

Send folder with contents <code>scp -rp out root@142.93.232.180:~/out</code> Notes:
- my avarage view time is 4.8s
- max time 34.4s
- min time 1.02

### Other
historyreader.py
Shows chart of training results.
scp