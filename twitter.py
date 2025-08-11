import tweepy

bearer_token = "AAAAAAAAAAAAAAAAAAAAAPS23QEAAAAAJFyR01yRGuMiLqjAI%2ByPlP7boOQ%3DtGdN5O30NzP8xnjsyzouVOBmVpmraMB32XneEFvEHhSUzN4NtL"
client = tweepy.Client(bearer_token)

class MyStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(tweet.text)

stream = MyStream(bearer_token=bearer_token)
stream.add_rules(tweepy.StreamRule("elon musk"))  # Filter for "elon musk"
stream.filter()