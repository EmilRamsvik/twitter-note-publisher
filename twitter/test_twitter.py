import pytest
import unittest
import tweepy
import numpy as np
from config import settings
from unittest import mock
from post_tweet import (
    divide_into_tweet,
    authenticate_twitter,
    get_airtable_data,
    post_tweet,
    send_tweets_to_twitter,
)


def test_divide_into_tweet():
    """
    Test that the divide_into_tweet function divides a string into a list of tweets
    that are less than or equal to 276 characters long.
    """
    quote = "This is a short tweet. This is a short tweet."
    tweets = divide_into_tweet(quote)
    assert len(tweets) == 1
    assert len(tweets[0]) <= 276


def test_more_than_one_tweet():
    """
    Test that the divide_into_tweet function divides a string into a list of tweets
    that are less than or equal to 276 characters long.
    """
    quote = "This is a sentence of fourty characters." * 8  # 280 characters.
    print(len(quote))
    tweets = divide_into_tweet(quote)
    assert len(tweets) == 2
    assert len(tweets[0]) <= 276
    assert len(tweets[1]) <= 276
    assert len(tweets[0]) + len(tweets[1]) == len(quote)
    assert (
        tweets[0][-1] == "."
    )  # Ensure that the last character is a period of first tweet.


def test_get_airtable_data(mocker):
    """
    Test that the get airtable data returns the data from the api, by mocking the
    response of the pyairtable.Table and pyairtable.table.all method.
    """
    # Fake parameters
    airtable_key = "super-secret-key"
    base_id = "app3q3q3q3q3q3q3q"
    table_name = "Quotes"

    mock_pyairtable = mocker.Mock(return_value="ok")  # mock pyairtable.Table
    mock_pyairtable.all = mocker.Mock(
        return_value=[
            dict(
                fields=dict(
                    Author="John Doe",
                    Title="A title",
                    Quote="This is a quote",
                    Posted=0,
                ),
                id="rec3q3q3q3q3q3q3q",
            )
        ]  # creates a list of records of len 1 with fields and id of the record
    )
    with mock.patch("post_tweet.Table") as mock_table:
        mock_table.return_value = mock_pyairtable
        airtable_field_id, author, title, quote = get_airtable_data(
            airtable_key, base_id, table_name
        )
        assert airtable_field_id == "rec3q3q3q3q3q3q3q"
        assert author == "John Doe"
        assert title == "A title"
        assert quote == "This is a quote"


def test_authenticate_twitter(mocker):
    """
    Test that the authenticate_twitter function tries to authenticate using API.
    """
    with mock.patch("post_tweet.tweepy.API") as mock_tweepy:
        mock_tweepy.return_value = "ok"
        auth = authenticate_twitter()
        assert auth == "ok"
        mock_tweepy.assert_called_once()


def test_send_tweet_to_twitter(mocker):
    """
    Test that the send_tweet_to_twitter function calls on update status api 
    for all tweets and the reference tweet.
    """
    mock_api = mock.Mock()
    mock_api.update_status = mock.Mock(
        return_value=mock.Mock(id=12345)
    )  # make new mock instance for each test case.
    with mock.patch("post_tweet.tweepy.API") as mock_tweepy:
        mock_tweepy.return_value = mock_api
        send_tweets_to_twitter(
            tweets=["tweet1", "tweet2"],
            reference="This is a reference string",
            api=mock_api,
        )
        mock_api.update_status.call_count == 3  # 2 tweets & 1 reference.


def test_post_tweet():
    """
    Tests the entire pipeline for sending tweets to twitter.
    """
    quotes = [
        "This is a single tweet quote",
        "This quote that must be split into 2 tweets" * 10,
        "This quote that must be split into 3 tweets" * 18,
    ]
    for quote in quotes:
        mock_api = mock.Mock()
        mock_api.update_status = mock.Mock(
            return_value=mock.Mock(id=12345)
        )  # make new mock instance for each test case.
        with mock.patch(
            "post_tweet.authenticate_twitter", mock.Mock(return_value=mock_api)
        ) as mock_auth:
            with mock.patch(
                "post_tweet.get_airtable_data",
                mock.Mock(return_value=("id", "author", "title", quote)),
            ) as mock_get_airtable_data:
                with mock.patch(
                    "post_tweet.Table.batch_update", mock.Mock(return_value="ok")
                ) as mock_update:
                    post_tweet()
                    mock_auth.assert_called_once()
                    mock_get_airtable_data.assert_called_once()
                    assert (
                        mock_api.update_status.call_count
                        == np.ceil(len(quote) / 276) + 1
                    )  # called (number of tweets + reference) number of times
