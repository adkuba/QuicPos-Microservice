# Table of Contents
- [What I've learned](#what-ive-learned)
- [Important](#important)
- [Twitter](#twitter)
    - [Query](#query)
    - [API](#api)
    - [Saving](#saving)
- [Machine learning](#machine-learning)
    - [Recommender structure](#recommender-structure)
    - [Detector structure](#detector-structure)
    - [Training](#training)



# What I've learned
- Data science in **Python**
- Working with **Twitter API** and **MongoDB**
- How to design, create and train ML model in **Tensorflow**



# Important
- To open database in mongo shell, type: <code>mongo "mongodb+srv://quicpos.felpr.gcp.mongodb.net/quicpos" --username admin</code>
- Create <code>passwords.py</code> file with Mongo SRV, general password and SSH server password
- [historyreader.py](historyreader.py) - shows chart of training results.
- Send folder with contents <code>scp -rp out root@142.93.232.180:~/out</code>



# Twitter
All initial data in QuicPos is from Twitter. I was using [Recent search endpoint](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent) to get tweets by query. Then I parsed text and images from downloaded tweets and send it to my server.

### Query
Using [trends.py](trends.py). Question: how to create many good queries to search tweets and get versatile and reliable results? Answer: Create queries with Google trends - Python package. Trends categories I was using:
* Top searches for selected years and countries
* Now trending for selected countries
* Related keywords for above categories
Finally, I translated generated keywords to English using Google Translate - also Python package and then saved it to <code>keywords-temp.txt</code>.

### API
Using [twitter.py](twitter.py) - data fetch. Additional notes to created Twitter queries:
* Example response out in [data.json](data.json)
* Script waits between queries to not overpass rate limits

Example query to Twitter API:
```sh
curl -X GET -H "Authorization: Bearer AAAAAAAAAAAAAAAAAAAAAFJmJAEAAAAAiKXgs71WHr8Ay76lBSPzZfDBIOo%3DZH4yblNSZC1J4YUNIrLpW8mWaeZRDtUQDUrm83NLmuQM1wmxnq" "https://api.twitter.com/2/tweets/20"
```

### Saving
Using [saver.py](saver.py). Parses json tweets from data folder to my server. Steps
* Text parsing - remove hashtags and annotations.
* Image download and convert to base64 string.

To check how much space is used in cloud storage, execute: <code>gsutil du -sh gs://quicpos-images/</code> may be with watch command.



# Machine learning
Neural nets notes. See issues and commit history of python net generators file to learn more about previous ideas. About text preprocessing: [notes](https://github.com/adkuba/QuicPos-Server/issues/4#issuecomment-720122145).

### Recommender structure
Using [generate-recommender.py](#generate-recommender.py) generate recommender neural net. 

#### First verion keypoints:
* Input: all post fields also with 224x224x3 image and requesting user details. UserID's as ints - based on internal server counter. Example first user has int=0 second int=1... Text converted to ascii int representation.
* Output: 5 classes (very_bad_view, bad_view, avarage_view, good_view, excellent_view) describing amount of time spent on selected post.
* Disadvantages: UserID's as counter was unstable - duplicate userIDs after some time. To much data in input - full views array, full image, text as ascii etc. was to much for the neural net to find some kind of patterns. Long processing times - because of large input. Unclear output.

#### Current version keypoints:
* Input: post text as words indexes in my dictionary and preprocessed by mobilenet image (1280 float features vector). UserID's changed to string UUID, for net input I convert UUID to 4 Ints (UUID to bytes -> bytes to ints).
* Output: Recommend post or not (0 or 1).
* Disadvantages: UserID's still may be unclear. This net prefers only posts with images.

Future version: [issue](https://github.com/adkuba/QuicPos-Microservice/issues/4), somehow relate requesting user with post's creator user and post's content.

### Detector structure
Using [generate-detector.py](generate-detector.py) generate spam detector neural net. First and current version is almost identical to recommender net. Current version seems accurate. Future version: detect type of spam.

### Training
Using [train-detector.py](train-detector.py) [train-recommender.py](train-recommender.py) and [dictionary.py](dictionary.py). Steps:
* Download data from Mongo database
* Parse data for training
* Make generator for training batches
* Train neural net
* Send and replace current ML model
* Wait and repeat process

Important, Go Tensorflow package version 1.15 has memory leak when loading new models! [Issue](https://github.com/adkuba/QuicPos-Server/issues/11)