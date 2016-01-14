#! /usr/bin/env python

# This script uses the _twitter_ library to access the Twitter REST API
# the code is based on an original script provided by CB.

# The queries below should be adapted as required.

# Authentication configuration needs to be stored in config_params.json
# config_params.json must be of the form:
# {
#   "consumer_key" : "<consumer key>",
#   "consumer_secret" : "<consumer secret key>",
#   "access_token" : "<access token key>",
#   "access_token_secret" : "<access token secret key>"
# }

# libraries import
import json, twitter, time, sys, math

# Function to move along the tweets list for available ids
#' @r = tweet list
def getNextID( r ) :
    min_id = r[0]['id']
    for tweet in r :
        if tweet['id'] < min_id :
            min_id = tweet['id']
    return min_id

# Function to capture all tweets into an array
def getTweets(r) :
    tweets = []
    for i in range( len( r ) ) :
        tweet = {}
        tweet['id'] = r[i].id
        tweet['date'] = r[i].created_at
        tweet['text'] = r[i].text.replace( "\n", " " )
        tweet['latitude'] = float( r[i].geo['coordinates'][0] )
        tweet['longitude'] = float( r[i].geo['coordinates'][1] )
	tweet['user'] = r[i].user.id
        tweets.append( tweet.copy() )
    return tweets

# Get the json authentication parameters
def get_config_params ( filepath ) :
    with open( filepath, 'r') as data_file :
        return json.load( data_file )

## Main process
if __name__ == '__main__' :
    sys.stdout.write( '0%' )
    sys.stdout.flush()

    # Get API keys
    config_params = get_config_params( 'config_params.json' )

    # Maybe an unnecessary step...

    consumer_key = config_params[ 'consumer_key' ]
    consumer_secret = config_params[ 'consumer_secret' ]
    access_token = config_params[ 'access_token' ]
    access_token_secret = config_params[ 'access_token_secret' ]


    # Access the API
    api = twitter.Api(
        consumer_key = consumer_key,
        consumer_secret = consumer_secret,
        access_token_key = access_token,
        access_token_secret = access_token_secret
    )

    # Import the tweets
    # Get the initial batch of results
    # the results can only be obtained in batches of a bit more than
    # 100 tweets. We're rounding to 100 tweets batches. 
    #
    # Coordinates 51.5, -0.1 correspond to London
    results = getTweets( api.GetSearch(
        geocode = ( 51.5, -0.1, '10mi' ), 
        count = 100
    )
    )
    # Get the subsequent batches of results
    next_id = getNextID( results )
    for i in range( 150 ) :
        flag = 0
        try:
            next_results = getTweets( api.GetSearch(
                geocode = ( 51.5, -0.1, '10mi' ),
                count = 100,
                max_id = next_id  # reference to get sequenced batches
            )
            )
            next_id = getNextID( next_results )
        except twitter.error.TwitterError:
            print "error"
            next_id = next_id - 1

        results += next_results
        sys.stdout.write(
            '\b' * (len(str(int(math.floor(i * 100 / 151 )))) + 1 )
            + str(int(math.floor((i + 1) * 100 / 151 ))) + '%')
        sys.stdout.flush()
    
    with open('outcome_tweets.json', 'w') as outcome_file:
        json.dump( results, outcome_file )

    print('Collected ' + str(len( results )) + ' tweets')
