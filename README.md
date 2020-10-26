# QuicPos-Microservice
Machine learning workflow, python microservice.

## twitter.py
Data fetch from twitter - initial data for my service.
* Warning, end-time works max 1 week back, good value - 1/2 week back
* Look where is image url - see in data.json
* I can set in future to get max 100 tweets, not only 10
* Links [doc](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent)

### TODO
I need to have pure text with links and image.
* Save smaller image for neural net in server!!!
* Download image, delete hashtags, annotations and save post object with graphql
* Integrate google trends and automatic data fetch!