# from helpers.simpleDate import Date
from queries import QueryManager
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from hashlib import sha256
import snscrape.modules.twitter as sntwitter
import pandas as pd
import os
import subprocess
import json
import re
from datetime import datetime, date, timedelta
from multiprocessing import Pool, Process


# ! Has to be run while working directory is the twint-zero folder.

class OzpScraper():

    """A not so flexible class built for the express purpose of running the queries from queries.py"""

    def __init__(self, identifier, fileLocation):
        self.vader = SentimentIntensityAnalyzer()
        self.qm = QueryManager()
        self.queryCatList = ["gambling", "gacha", "lootbox"]
        self.identifier = identifier
        self.fileLocation = fileLocation


    def runQueries(self, queryCat):
        """
        runQueries takes a group, retrieves the relevant query and then tries to execute it.
        Results are stored in the relevant csv file, if the query fails before completion,
        it can be continued via continueQuery.
        """
        print(f"running {queryCat}")

        query = self.qm.generateQueryFromCat(queryCat)
        output_path = f"{self.fileLocation}{queryCat}-{self.identifier}.csv"

        self._runTwintQuery(query, output_path)

        print(f"Finished running query for: {queryCat}")
        return True

    def continueQuery(self, queryCat):
        """
        continueQuery looks for a relevant csv file and checks whether or not it has reached
        the expected end date for what should be scraped. If not it tries to restart the 
        scraping process from the last registered date.
        """
        output_path = f"{self.fileLocation}{queryCat}-{self.identifier}.csv"
        previousDate = findLastDate(output_path)

        while (previousDate != "2022-01-01"):
            print(f"Continuing query for {queryCat}")
            query = self.qm.generateQueryFromCat(queryCat, previousDate)
            self._runTwintQuery(query, output_path)
            print(f"Query for {queryCat} has finished, check completion...")

            previousDatePrime = previousDate
            previousDate = findLastDate(output_path)
            if previousDatePrime == previousDate:
                print("Crashed twice on the same date")
        print(f"Scrape of {queryCat} has reached 2022-01-01")
        return True

    def _runTwintQuery(self, query, output_path):
        """
        Hidden function (except we're in python) which powers run and continue query. Transforms the actual
        query into a twint-zero command to execute via the subprocess library. Each retrieved tweet is processed
        and put into the given csv file.
        """
        resultDict = self._newResultDict()
        print(f"QUERY: {query}")
        scrape_lst = ["go", "run", "main.go",
                      "-Query", query, "-Format", "json"]
        skippedTweets = 0
        with subprocess.Popen(scrape_lst, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, encoding="utf-8") as p:
            for i, line in enumerate(p.stdout):
                tweet = json.loads(line)

                if i % 1500 == 0 and i > 1:
                    # print(f"Saving dict of size: {sys.getsizeof(resultDict)}")
                    df = pd.DataFrame(resultDict)
                    df.to_csv(output_path, mode='a',
                              header=not os.path.exists(output_path))
                    resultDict = self._newResultDict()
                    timestamp = tweet["timestamp"][:-3]
                    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(
                        f"{currentTime}: updated {output_path} (newest entry - i: {i}, ts: {timestamp})")
                    print(f"total skipped = {skippedTweets}")

                try:
                    for tweetSn in sntwitter.TwitterTweetScraper(tweet["id"]).get_items():
                        self._processTwintTweet(tweet, tweetSn, resultDict)
                except:
                    skippedTweets += 1
            exit_code = p.poll()

        df = pd.DataFrame(resultDict)
        print(df.head())
        df.to_csv(output_path, mode='a',
                  header=not os.path.exists(output_path))

        return exit_code

    def scrapeGeneral(self, amount):
        """
        Alternative verion of runQuery which instead of scraping tweets for any particular topic,
        scrapes tweets about any topic up to a specified amount of tweets per day.
        """
        output_path = f"{self.fileLocation}general-{self.identifier}.csv"

        start_date = date(2022, 1, 1)
        end_date = date(2023, 1, 1)
        daterangeL = daterange(start_date, end_date)
        print("Performing general scrape")
        # For each day in the year
        for i, curDate in enumerate(daterangeL):
            # Create a general query (lang:en get's you every english tweet even with an empty body)
            since = curDate.strftime("%Y-%m-%d")
            until = (curDate + timedelta(1)).strftime("%Y-%m-%d")
            query = self.qm.createFullQuery(
                "", dateQuery=f"since:{since} until:{until}")

            self._runTwintQuerySetAmount(query, output_path, amount)
        print("EZ, DONE")

    def _runTwintQuerySetAmount(self, query, output_path, amount):
        
        """
        Hidden function to aid scrapeGeneral and create the actual relevant twint-zero
        / sub process operations.
        """
        resultDict = self._newResultDict()
        scrape_lst = ["go", "run", "main.go",
                      "-Query", query, "-Format", "json"]
        skippedTweets = 0
        while (len(resultDict["date"]) < (amount-4)):
            resultDict = self._newResultDict()
            with subprocess.Popen(scrape_lst, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, encoding="utf-8") as p:
                for i, line in enumerate(p.stdout):

                    tweet = json.loads(line)
                    try:
                        for tweetSn in sntwitter.TwitterTweetScraper(tweet["id"]).get_items():
                            self._processTwintTweet(tweet, tweetSn, resultDict)
                    except:
                        skippedTweets += 1

                    if i >= amount-1:
                        break
                p.terminate()
                p.wait()

        df = pd.DataFrame(resultDict)
        df.to_csv(output_path, mode='a',
                  header=not os.path.exists(output_path))
        timestamp = resultDict["date"][-1]
        currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{currentTime}: updated {output_path} (newest entry - ts: {timestamp})")
        print(f"total skipped = {skippedTweets}")

        return True

    

    """
    Helpers classes to process individual tweet after it is provided.
    """

    def _processTwintTweet(self, tweetDict, tweetObj, result):
        """
        Processes a tweet found via twint-zero to extract relevant data and store it.
        """
        # Get tweet meta data
        date = tweetObj.date.date()
        result["date"].append(date)

        isRetweet = tweetObj.retweetedTweet != None
        result["isRetweet"].append(isRetweet)

        isReply = tweetObj.inReplyToTweetId != None
        result["isReply"].append(isReply)

        containsMedia = tweetDict["attachments"] != []
        result["containsMedia"].append(containsMedia)

        tweetLength = len(tweetDict["text"])
        result["tweetLength"].append(tweetLength)

        # Hash user to be used for (for example) tweets/user data
        userHash = hashUserName(tweetObj.user.username)
        result["userHash"].append(userHash)

        # Calculate sentiment

        score = self.vader.polarity_scores(tweetObj.rawContent)
        result["neg"].append(score["neg"])
        result["neu"].append(score["neu"])
        result["pos"].append(score["pos"])
        result["compound"].append(score["compound"])

        # Twitter search seems to return results based on: tweet content, username of poster, username of user being replied to (last one is included in rawcontent)
        searchedTexts = [tweetObj.rawContent,
                         tweetObj.user.username, tweetObj.user.displayname]
        self.qm.detectGameInTweet(' '.join(searchedTexts), result)

    def _newResultDict(self):
        resultDict = {
            "compound": [],
            "neg": [],
            "neu": [],
            "pos": [],
            "isReply": [],
            "isRetweet": [],
            "containsMedia": [],
            "tweetLength": [],
            "userHash": [],
            "date": [],
        }
        for game in self.qm.gamesList:
            resultDict[game] = []
        return resultDict


def hashUserName(userName):
    bytesVersion = bytes(userName, 'utf-8')
    return sha256(bytesVersion).hexdigest()  # hashed using sha256


"""
Helpers classes to find where the previous query failed and determine from which date to continue on.
"""


def tail(f, lines=20):  # https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-similar-to-tail
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0, 0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b'\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b''.join(reversed(blocks))
    return b'\n'.join(all_read_text.splitlines()[-total_lines_wanted:])


def findLastDate(fileName):
    f = open(fileName, 'rb')
    # not 1 to provide margin of error for blank lines missing data etc.
    last_lines = tail(f, lines=5)
    last_date = re.findall(r"\d{4}-\d{2}-\d{2}", str(last_lines))[-1]
    return last_date


def daterange(start_date, end_date):
    for n in reversed(range(int((end_date - start_date).days))):
        yield start_date + timedelta(n)
