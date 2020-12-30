"""
This script will delete all tweets before 2020. I have used an existing script from
https://gist.github.com/davej/113241 and the documentation from http://docs.tweepy.org/en/latest/getting_started.html

You will need to get a consumer key and consumer secret token to use this
script, you can do so by registering a twitter application at https://dev.twitter.com/apps
You also need to download all your twitter data from your twitter account in order to know when the
@requirements: Python 2.5+, Tweepy (http://pypi.python.org/pypi/tweepy/3.9.0)
@author: Daniel Bueno Pacheco
"""
import tweepy
import json
from dateutil.parser import parse

MAX_TWEETS_PER_REQUEST = 100
YEAR_MAX = 2020  # I want to delete all the tweets before 2020


class Credentials:
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""


def read_tweets_json():
    """Read json that contains all the information from all the tweets I have written."""

    tweets_id = []
    try:
        with open("..\\twitter-2020-12-14-data\\data\\tweet.js", 'r', encoding="utf-8") as f:
            tweets_str = "".join(f.readlines())
            # In order to transform to json we delete this part
            tweets_str = tweets_str.replace("window.YTD.tweet.part0 = ", "")
            json_tweets = json.loads(tweets_str)

        for tweet in json_tweets:
            tweet_date = parse(tweet['tweet']['created_at'])
            if tweet_date.year >= YEAR_MAX:
                continue
            tweets_id.append(tweet['tweet']['id'])

    except EnvironmentError:
        print("Error loading tweet.js")

    return tweets_id


def read_keys_file():
    """Read credentials from file to authenticate in Twitter"""

    try:
        with open("keys.txt") as f:
            for line in f:
                line = line.replace("\t", "")
                line = line.replace("\n", "")
                line = line.replace(" ", "")
                if line.find("CONSUMER_KEY=") != -1:
                    Credentials.consumer_key = line.split("=")[1]
                elif line.find("CONSUMER_SECRET_KEY=") != -1:
                    Credentials.consumer_secret = line.split("=")[1]
                elif line.find("ACCESS_TOKEN=") != -1:
                    Credentials.access_token = line.split("=")[1]
                elif line.find("ACCESS_TOKEN_SECRET=") != -1:
                    Credentials.access_token_secret = line.split("=")[1]
    except EnvironmentError:
        print("Error opening keys.txt file.")


def oauth_login():
    """Authenticate with twitter using OAuth"""
    read_keys_file()  # read credentials from file

    auth = tweepy.OAuthHandler(Credentials.consumer_key, Credentials.consumer_secret)
    auth.set_access_token(Credentials.access_token, Credentials.access_token_secret)

    return tweepy.API(auth)


def batch_delete(api):
    """ We delete all tweets before YEAR_MAX """
    id_ = read_tweets_json()
    with open("tweetsText.txt", "wb") as textTweetFile:
        for i in range(0, len(id_), MAX_TWEETS_PER_REQUEST):
            id_part = id_[i:MAX_TWEETS_PER_REQUEST+i]
            statuses = api.statuses_lookup(id_part)  # 100 tweets per request
            for status in statuses:
                try:
                    api.destroy_status(status.id)
                    text_tweet = str(status.text)
                    text_tweet = text_tweet.lower()
                    line = "Tweet " + str(status.id) + " deleted\t" + str(
                        text_tweet) + "\n" + "-------------------------------------\n"
                    line = line.encode('utf-8')
                    textTweetFile.write(line)
                except Exception as errDelete:
                    line = "Error " + str(errDelete) + "\nFailed to delete: " + str(status.id)
                    line = line.encode('utf-8')
                    textTweetFile.write(line)


if __name__ == "__main__":
    try:
        batch_delete(oauth_login())
    except Exception as err:
        print("Error: ", err)
