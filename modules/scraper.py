from helpers.simpleDate import Date
from modules.queries import QueryManager 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from snscrape.modules.twitter import sntwitter
import pandas as pd
import regex as re

class OzpScraper():

    """A not so flexible class built for the express purpose of running a specific set of queries without breaking.
    Hopefully."""

    def __init__(self, categories=["gambling", "gacha", "lootboxes", "general"], additionalQueries={}, year=2022, fileSuffix=""):
        self.vader = SentimentIntensityAnalyzer()
        self.qm = QueryManager()
        self.queryCatList = ["gambling", "gacha", "lootbox", "general"]

    def runQueries(self, identifier):
        for queryCat in self.queryList:
            query = self.qm.generateQueryFromCat(queryCat)
            self._runQuery(query, identifier)
            print(f"Finished running query for: {queryCat}")
        return True

    def continueQueries(self, identifier):
        pass #TODO find point to pick up from based on existing files and last entry in said file

    def _runQuery(self, query, identifier):
        # Scraping tweets
        resultDict = self._newResultDict()
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            #TODO implement in between saving for larger dict sizes, save every 1000 or so items
            #TODO implement progress indicator
            
            self._processTweet(tweet, resultDict)

        #Save results
        df = pd.DataFrame(resultDict)
        print(df.head())
        df.to_csv(f'{queryCat}.csv')
        return

    def _processTweet(self,tweet, result):
        # Get tweet meta data
        date = tweet.date.date()
        isRetweet = False if tweet.retweetedTweet == None else True
        isReply = False if tweet.inReplyToTweetId == None else True
        containsMedia = None # TODO implement this (photo, video, polls etc)
        
        # Hash user to be used for (for example) tweets/user data
        userHash = None # TODO implement this
        # Find keywords for each tweet
        keywords = self.qd.detectKeywords(tweet.rawContent) # TODO should also look at usernames (and just generally should be better)
        # Calculate sentiment
        score = self.vader.polarity_scores(tweet.rawContent) 
        
        # Store results in df/dict
        result["date"].append(tweet.date.date())
        result["neg"].append(score["neg"])
        result["neu"].append(score["neu"])
        result["pos"].append(score["pos"])
        result["compound"].append(score["compound"])
        result["isRetweet"].append(isRetweet)
        result["isReply"].append(isReply)
        result["keyWords"].append(keywords)

    def _newResultDict():
        return {"compound": [], 
                "neg": [], 
                "neu": [], 
                "pos": [], 
                "keyWords": [],
                "isReply": [],
                "isRetweet": [],
                "containsMedia": [],
                "tweetLength": [],
                "userHash": [],
                "date": [],
                }
    

    