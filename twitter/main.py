from post_tweet import post_tweet


def run(request):
    # request_json = request.get_json()
    post_tweet()
    print("Tweet posted successfully")
    return "Tweet posted successfully"


#
