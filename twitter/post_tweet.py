import tweepy
from config import settings
from pyairtable import Table
from typing import List


def divide_into_tweet(text: str) -> List[str]:
    """Takes a textstring and divides it unto a list of strings that are less
    than or equal to 276 characters long.

    Args:
        text (str): text to be divided into tweets

    Returns:
        List[str]: list of tweets less than 276
    """
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


def authenticate_twitter() -> tweepy.API:
    """Generates an api object that can be used to post tweets.

    Returns:
        tweepy.API: Authenticated twitter api object.
    """
    auth = tweepy.OAuthHandler(
        settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET
    )
    auth.set_access_token(
        settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET
    )
    return tweepy.API(auth)


def send_tweets_to_twitter(tweets: List[str], reference: str, api: tweepy.API):
    """Post tweets to the twitter account. If more than one tweet divides into
       a tweet string that is enumerated.

    Args:
        tweets (List[str]): list containing tweet length text strings.
        reference (str): reference to the source of the quote.
        api (tweepy.API): Authenticated twitter api object.
    """
    first_tweet = None
    number_of_tweets = len(tweets)
    if len(tweets) == 1:  # if only one tweet do not add numbering only reference
        first_tweet = api.update_status(f"{tweets[0]}")
        api.update_status(f"{reference}", in_reply_to_status_id=first_tweet.id)
    else:  # if more than one tweet add numbering, then add reference last
        counter = 0
        for tweet in tweets:
            counter = counter + 1
            if first_tweet is None:
                first_tweet = api.update_status(
                    f"{tweet} ({counter}/{number_of_tweets})"
                )
            else:
                api.update_status(
                    f"{tweet} ({counter}/{number_of_tweets})",
                    in_reply_to_status_id=first_tweet.id,
                )
        api.update_status(f"{reference}", in_reply_to_status_id=first_tweet.id)


def get_airtable_data(airtable_key: str, base_id: str, table_name: str):
    """Retrieves a table from airtable.

    Args:
        base_id (str): base_id - found in airtable
        airtable_key (str): used to be authorized to access airtable.
        table_name (str): name of the table beloning to the base_id

    Returns:
        tuple: (airtable_field_id, author, title, quote)
    """
    table = Table(api_key=airtable_key, base_id=base_id, table_name=table_name,)
    # loops through records until one that is not posted is found.
    for record in table.all():
        if record["fields"]["Posted"] == 0:
            break
        else:
            continue
    airtable_field_id = record["id"]
    author = record["fields"]["Author"]
    title = record["fields"]["Title"]
    quote = record["fields"]["Quote"]
    return airtable_field_id, author, title, quote


def post_tweet():
    """
    Posts a tweet to Twitter:

    1. Get twitter api handler
    2. Get data from airtable
    3. Divide quote into tweets
    4. Post tweet string to twitter
    """
    api = authenticate_twitter()  # get twitter account
    airtable_field_id, author, title, quote = get_airtable_data(
        base_id=settings.AIRTABLE_BASE_ID, table_name="Tweets"
    )
    tweets = divide_into_tweet(quote)
    reference = f"Taken from {title} by {author}"
    send_tweets_to_twitter(tweets, reference, api)
    Table(
        api_key=settings.AIRTABLE_API_KEY,
        base_id=settings.AIRTABLE_BASE_ID,
        table_name="Tweets",
    ).batch_update(
        records=[{"id": airtable_field_id, "fields": {"Posted": 1}}]
    )  # update airtable that the tweet has been posted.
