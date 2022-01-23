# This is the script that runs when the gcp function is triggered.

from twitter.post_tweet import post_tweet


def hello_world(request):
    request_json = request.get_json()
    post_tweet()
    print("Tweet posted successfully")
