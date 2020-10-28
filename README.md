# QuicPos-Microservice
Machine learning workflow, python microservice.

## twitter.py
Data fetch from twitter - initial data for my service.
* Warning, end-time works max 1 week back, good value - 1/2 week back or full because there may not be many tweets in selected topic
* Look where is image url - see in data.json
* I can set in future to get max 100 tweets, not only 10, 10-20 tweets per keyword is good
* Links [doc](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent)

### TODO
I need to have pure text with links and image.
* Clean keywords from duplicates!
* Download image, delete hashtags, annotations from example data.json
* Full integration: use keywords.txt and save post object with graphql, delete duplicate tweets by id!!! save tweets to file(?)