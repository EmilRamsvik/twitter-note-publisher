import tweepy
from config import settings
from pyairtable import Table


def divide_into_tweet(text):
    puncts = [".", ",", ";", "--"]
    tweets = []
    while len(text) > 280:
        cut_where, cut_why = max((text.rfind(punc, 0, 276), punc) for punc in puncts)
        if cut_where <= 0:
            cut_where = text.rfind(" ", 0, 276)
            cut_why = " "
        cut_where += len(cut_why)
        tweets.append(text[:cut_where].rstrip())
        text = text[cut_where:].lstrip()
    tweets.append(text)
    return tweets


def post_tweet():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(
        settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET
    )
    auth.set_access_token(
        settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)

    table = Table(
        api_key=settings.AIRTABLE_API_KEY,
        base_id=settings.AIRTABLE_BASE_ID,
        table_name="Tweets",
    )
    for record in table.all():
        if record["fields"]["Posted"] == 0:
            break
        else:
            continue
    airtable_field_id = record["id"]
    author = record["fields"]["Author"]
    title = record["fields"]["Title"]
    quote = record["fields"]["Quote"]
    tweets = divide_into_tweet(quote)
    reference = f"Taken from {title} by {author}"
    first_tweet = None
    counter = 0
    number_of_tweets = len(tweets)
    if len(tweets) == 1:
        first_tweet = api.update_status(f"{tweets[0]}")
        api.update_status(f"{reference}", in_reply_to_status_id=first_tweet.id)
    else:
        for tweet in tweets:
            counter = counter + 1
            if first_tweet is None:
                first_tweet = api.upde_status(f"{tweet} ({counter}/{number_of_tweets})")
            else:
                api.update_status(
                    f"{tweet} ({counter}/{number_of_tweets})",
                    in_reply_to_status_id=first_tweet.id,
                )
        api.update_status(f"{reference}", in_reply_to_status_id=first_tweet.id)
        print(tweets)
    table.batch_update(records=[{"id": airtable_field_id, "fields": {"Posted": 1}}])

