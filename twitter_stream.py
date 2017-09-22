import os
import oauth2 as oauth
import urllib2 as urllib


API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
ACCESS_TOKEN_KEY = os.environ["ACCESS_TOKEN_KEY"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

_debug = 0

oauth_token = oauth.Token(key=ACCESS_TOKEN_KEY, secret=ACCESS_TOKEN_SECRET)
oauth_consumer = oauth.Consumer(key=API_KEY, secret=API_SECRET)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_handler = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)


def twitter_request(url, parameters, http_method="GET"):
    """
    Construct, sign, and open a twitter request
    using the hard-coded credentials above.
    """
    req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                                token=oauth_token,
                                                http_method=http_method,
                                                http_url=url,
                                                parameters=parameters)

    req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

    if http_method == "POST":
        encoded_post_data = req.to_postdata()
    else:
        encoded_post_data = None
        url = req.to_url()

    opener = urllib.OpenerDirector()
    opener.add_handler(http_handler)
    opener.add_handler(https_handler)

    response = opener.open(url, encoded_post_data)

    return response


def fetch_samples():
    # url = "https://stream.twitter.com/1/statuses/sample.json"
    url = "https://api.twitter.com/1.1/search/tweets.json?q=software+diversity"
    parameters = []
    response = twitter_request(url, parameters)
    for line in response:
        print line.strip()


if __name__ == '__main__':
    fetch_samples()
