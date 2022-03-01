import requests
import json
import xmltodict
import numpy as np
import pandas
from transformers import pipeline

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAM76ZgEAAAAArUfhRKFZtet4rfTIUcXmoLP8HjA%3DdqRd6w12KVGaDE7lHuqWq7d3zaalMugEW2lAeCfXOcUVXSlShs"


async def search_twitter(query, tweet_fields,  bearer_token=BEARER_TOKEN):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&max_results=100".format(
        query, tweet_fields
    )
    response = await requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


async def search_google(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}"
    response = await requests.request("GET", url,)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.text


def sentiments(df):
    sentiment_pipeline = pipeline("sentiment-analysis")
    temp = []
    for d in df["Title"]:
        temp.append(sentiment_pipeline(d)[0]["score"])
    df["Sentiment Score"] = temp
    return df


# List for Collecting data from Twitter and Google
collection = []

# search term
query = "green hydrogen"

# twitter fields to be returned by api call
tweet_fields = "tweet.fields=text,author_id,created_at"

# twitter api call
json_response = search_twitter(
    query=query, tweet_fields=tweet_fields, bearer_token=BEARER_TOKEN)
# pretty printing
res = json.dumps(json_response["data"], indent=4, sort_keys=True)
for a in json_response["data"]:
    collection.append(np.array([a["created_at"], a["text"], a["author_id"]]))


# Google RSS api call
json_response = search_google(
    keyword=query)
res = xmltodict.parse(json_response)
for a in res["rss"]["channel"]["item"]:
    collection.append(
        np.array([a["pubDate"], a["title"], a["source"]["#text"]]))


df = pandas.DataFrame(data=collection, columns=[
    "Date", "Title", "Source"])
df = sentiments(df)
df.to_csv("sample.csv")
