# -*- coding: utf-8 -*-
"""
Derive the sentiment of each tweet
"""
import sys
import json
from itertools import chain

# from nltk.util import ngrams

MAX_NGRAMS_DEGREE = 3

MOCK_TWEETS = [{'text': "can't stand in love"}, \
               {'text': 'the cool stuff is not that cool'}, \
               {'text': "cashing in and love me, but dont like me"}, \
               {"text": "it does not work. fix it up!!"}, \
               {'text': "I was naïve once-in-a-lifetime , \
        now I'm self-confident and walk in right direction"}, \
               {"text": "no fun, no screwed, screwed up. dont like!!! , like."}]


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
    tweets_scores = []
    for tweet in tweets['statuses']:
        if 'text' in tweet:
            text = tweet['text']
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
            tweets_scores.append(score)
    return tweets_scores


def parse_tweets(file_path):
    with open(file_path) as tweets_file:
        tweets = json.load(tweets_file)
    return tweets


def parse_sentiment_file(sentiment_file_path):
    with open(sentiment_file_path) as sent_file:
        scores = {}  # initialize an empty dictionary
        for line in sent_file:
            term, score = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
            scores[term] = int(score)  # Convert the score to an integer.
        return scores


def main():
    scores = parse_sentiment_file(sys.argv[1])
    tweets = parse_tweets(sys.argv[2])
    tweets_scores = get_sentiments(tweets, scores)
    print(tweets_scores)


if __name__ == '__main__':
    main()
