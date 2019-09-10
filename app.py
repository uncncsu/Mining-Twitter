import os
import sys
import csv
import tweepy
import matplotlib.pyplot as plt

from collections import Counter
from aylienapiclient import textapi

open_kwargs = {}

if sys.version_info[0] < 3:
    input = raw_input
else:
    open_kwargs = {'newline': ''}


# Twitter credentials
consumer_key = "Your consumer key here"
consumer_secret = "your secret consumer key here"
access_token = "your access token here"
access_token_secret = "your secret access token here"

# AYLIEN credentials
application_id = "923846fa"
application_key = "f79a2ec4748a67863e778d47c936a52c"

# set up an instance of Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# set up an instance of the AYLIEN Text API
client = textapi.Client(application_id, application_key)

#here insert a few lines to open the previous CSV file and read the last entry for id
max_id = 0

file_name = 'Sentiment_Analysis_of_Tweets_About_OLDTUFFY_query.csv'

if os.path.exists(file_name):
    with open(file_name, 'r') as f:
        for row in csv.DictReader(f):
            max_id = row['Tweet_ID']
else:
        with open(file_name, 'w', **open_kwargs) as f:
            csv.writer(f).writerow([
                                    "Tweet_ID",
                                    "Time",
                                    "Tweet",
                                    "Sentiment"])

results = api.search(
    lang="en",
    q="Old Tuffy -rt",
    result_type="recent",
    count=10,
    since_id=max_id
)

results = sorted(results, key=lambda x: x.id)
print("--- Gathered Tweets \n")

# open a csv file to store the Tweets and their sentiment
with open(file_name, 'a', **open_kwargs) as csvfile:
    csv_writer = csv.DictWriter(
        f=csvfile,
        fieldnames=[
                    "Tweet_ID",
                    "Time",
                    "Tweet",
                    "Sentiment"]
    )

    print("--- Opened a CSV file to store the results of your sentiment analysis... \n")

    # tidy up the Tweets and send each to the AYLIEN Text API
    for c, result in enumerate(results, start=1):
        tweet = result.text
        tidy_tweet = tweet.strip().encode('ascii', 'ignore')
        tweet_time = result.created_at
        tweet_id = result.id

        if not tweet:
            print('Empty Tweet')
            continue

        response = client.Sentiment({'text': tidy_tweet})
        csv_writer.writerow({
        	"Tweet_ID": tweet_id,
        	"Time": tweet_time,
            'Tweet': response['text'],
            'Sentiment': response['polarity'],
        })

        print("Analyzed Tweet {}".format(c))

# count the data in the Sentiment column of the CSV file
with open(file_name, 'r') as data:
    counter = Counter()
    for row in csv.DictReader(data):
        counter[row['Sentiment']] += 1

    positive = counter['positive']
    negative = counter['negative']
    neutral = counter['neutral']

# declare the variables for the pie chart, using the Counter variables for "sizes"
colors = ['green', 'red', 'grey']
sizes = [positive, negative, neutral]
labels = 'Positive', 'Negative', 'Neutral'

# use matplotlib to plot the chart
plt.pie(
    x=sizes,
    shadow=True,
    colors=colors,
    labels=labels,
    startangle=90
)

plt.title("Sentiment of {} Tweets about Your Subject".format(sum(counter.values())))
plt.show()