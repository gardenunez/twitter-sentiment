import os
import json
import requests
from requests_oauthlib import OAuth1


API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
ACCESS_TOKEN_KEY = os.environ["ACCESS_TOKEN_KEY"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

_debug = 0


def twitter_request(url):
    """
    Construct, sign, and open a twitter request
    using the hard-coded credentials above.
    """
    auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    response = requests.get(url, auth=auth)

    return response


def fetch_samples():
    url = "https://api.twitter.com/1.1/search/tweets.json?q=software+diversity"
    response = twitter_request(url)
    print(json.dumps(response.json()))


if __name__ == '__main__':
    fetch_samples()
