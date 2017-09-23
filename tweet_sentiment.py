# -*- coding: utf-8 -*-
"""
Derive the sentiment of each tweet
"""
import argparse
# from nltk.util import ngrams
import os
from itertools import chain

import tweepy

MAX_NGRAMS_DEGREE = 3

MOCK_TWEETS = [{'text': "can't stand in love"}, \
               {'text': 'the cool stuff is not that cool'}, \
               {'text': "cashing in and love me, but dont like me"}, \
               {"text": "it does not work. fix it up!!"}, \
               {'text': "I was naïve once-in-a-lifetime , \
        now I'm self-confident and walk in right direction"}, \
               {"text": "no fun, no screwed, screwed up. dont like!!! , like."}]

API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
ACCESS_TOKEN_KEY = os.environ["ACCESS_TOKEN_KEY"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]


def ngrams(sequence, n, pad_left=False, pad_right=False, pad_symbol=None):
    """ Return a sequence of ngrams from a sequence of items. """

    if pad_left:
        sequence = chain((pad_symbol,) * (n - 1), sequence)
    if pad_right:
        sequence = chain(sequence, (pad_symbol,) * (n - 1))
    sequence = list(sequence)

    count = max(0, len(sequence) - n + 1)
    return [tuple(sequence[i:i + n]) for i in range(count)]


def sanitize_text(text):
    result = ""
    g = lambda c: c.isalnum() or c in [u'-', u"'"]
    for char in text:
        try:
            if g(char):
                result = "%s%s" % (result, char)
            else:
                result = "%s " % result
        except UnicodeDecodeError:
            continue
    return result


def get_sentiments(tweets, scores):
    print('Getting sentiments ...')
    tweets_scores = {}
    for text in tweets:
        score = get_sentiment(scores, text)
        if score in tweets_scores:
            tweets_scores[score].append(text)
        else:
            tweets_scores[score] = [text]
    print('DONE ...')
    return tweets_scores


def get_sentiment(scores, text):
    text = sanitize_text(text)
    splitted_text = text.split()
    score_map = {}
    degree = range(min(len(splitted_text), MAX_NGRAMS_DEGREE) + 1, 0, -1)
    ignore_words = []
    for g in degree:
        ng = ngrams(splitted_text, g)
        for words in ng:
            term = ' '.join(words)
            if term in scores:
                # if multiple words term, ignore this ones if appears again
                if len(words) > 1:
                    ignore_words.extend(words)
                elif term in ignore_words:
                    ignore_words.remove(term)
                    continue
                if term in score_map:
                    score_map[term] += 1
                else:
                    score_map[term] = 1
    score = sum([scores[key] * value for key, value in score_map.items()])
    return score


def parse_tweets(file_path):
    with open(file_path) as tweets_file:
        tweets = tweets_file.readlines()
    return tweets


def parse_sentiment_file(sentiment_file_path):
    with open(sentiment_file_path) as sent_file:
        scores = {}  # initialize an empty dictionary
        for line in sent_file:
            term, score = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
            scores[term] = int(score)  # Convert the score to an integer.
        return scores


def twitter_request(query):
    """
    Construct, sign, and open a twitter request
    using the hard-coded credentials above.
    """
    print('Getting tweets ...')
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    tweet_texts = []
    try:
        for tweet in tweepy.Cursor(api.search, q=query,
                                   count=20, lang="en", since='2017-09-01').items():
            tweet_texts.append(tweet.text)
    except Exception as e:
        print(e)
    print('DONE ...')
    return tweet_texts


def download(args):
    texts = twitter_request(args.query)
    with open(args.destination, 'w') as output:
        output.writelines(texts)


def sentiment(args):
    scores = parse_sentiment_file(args.score_file)
    texts = parse_tweets(args.source_file)
    tweets_scores = get_sentiments(texts, scores)
    for key, values in tweets_scores.items():
        print(key, len(values))


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    download_parser = subparsers.add_parser('download')
    download_parser.add_argument('-q', dest='query', help='query')
    download_parser.add_argument('-d', dest='destination', help='destination file')
    download_parser.set_defaults(func=download)
    sent_parser = subparsers.add_parser('sentiment')
    sent_parser.add_argument('--score', dest='score_file', help='file with scores')
    sent_parser.add_argument('--source', dest='source_file', help='file to parse')
    sent_parser.set_defaults(func=sentiment)
    args = parser.parse_args()

    if args.func:
        args.func(args)


if __name__ == '__main__':
    main()
