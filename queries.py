import re
"""
This file serves to transform the tables given in Section 3 of my thesis into tables.

Notes on constructing queries:
each seperate word is automaticaly joined by AND token
words can be joined as a phrase using quotes ("hello there")
lang:xx filters to only include said language,
-(from:TestKitchen) excludes a specific account
"""


querySettingsDefault  = \
    "lang:en -filter:links" #-filter:links cuts out a lot of bots/advertisements #probably include replies TBH filter:replies, howe
queryBlackListDefault = \
    "-giveaway -codes -crypto -cryptocasino -nft -blockchain -eth -doge -btc"
queryTimeWindowDefault = \
    "until:2023-01-01 since:2022-01-01"

gameKeyCollection= {
    "gambling": {
            "Poker": "(poker)",
            "Roulette": "(roulette -\"russian roulette\")",
            "Blackjack": "(blackjack)",
            "Craps": "(craps)",
            "Scratch Lotteries": "(\"scratch off\" OR \"scratch lottery\" OR \"scratch card\")"
            },
    "gacha": {
            "Genshin Impact": "(genshin)",
            "Honkai (Series)": "(honkai)",
            "Arknights": "(arknights)",
            "Azur Lane": "(azurlane OR \"azur lane\")",
            "Granblue Fantasy": "(granblue)"
            },
    "lootbox": {
            "Fifa": "(fut OR fifa)",
            "Counter Strike": "(csgo)",
            "Apex Legends": "(apex -predator)",
            "Hearthstone": "(hearthstone)",
            "Clash Royale": "(\"clash royale\")",
            }, 
    "sportsBetting": {
            "Football": "(football)",
            "Basketball": "(nba)",
            "Cricket": "(cricket)"
    }
}

actionKeyCollection = {
    "gambling": "(gambl OR gamble OR gambling OR bet OR betting OR win OR won OR lose OR lost)",
    "gacha": "(pull OR roll OR gacha OR banner)", 
    "sportsBetting": "(gambl OR gamble OR gambling OR bet OR betting)",
    "lootbox": {"Fifa": "pack OR card",
            "Counter Strike": "crate OR case",
            "Apex Legends": "pack",
            "Hearthstone": "pack OR pull",
            "Clash Royale": "chest",
            
            } 
}

class QueryManager():  
    """ Class for creating queries using a keyword-actionword structure as well as
    for any functions which rely on that same query definition structure. """  

    def __init__(self):
        self.queryToKeywordDict = self.generateQueryToKeywordDict()
        self.gamesList = self.getAllGames()

    def getAllGames(self):
        """
        Provides a list containing each game included in the queries
        """
        games = []
        for keyList in gameKeyCollection.items():
            games.extend(list(keyList[1]))
        return games
    
    
    def generateQueryToKeywordDict(self):
        """
            Creates a dictionary with the following structure: 
                {"Fire Emblem: Heroes": ["feheroes", "fe_heroes", etc]}
            Which can then be looped over to extract which games are mentioned in tweets
        """
        queryToKeyDict = {}
        for gameList in gameKeyCollection.values():
            for game, keyString in gameList.items():
                gameKeys = self.seperateGameKeys(keyString)
                queryToKeyDict[game] = gameKeys
        return queryToKeyDict

    
    def generateQueryFromCat(self, cat, date = None):
        """
        Generates a query based on the given group (cat).
        """
        if cat == "general":
            defaultSuffix = "lang:en -filter:links" #-filter:links cuts out a lot of bots/advertisements #probably include replies TBH filter:replies, howe
            defaultFilters = "-giveaway -crypto -cryptocasino -nft -blockchain -eth -codes"
            return f"{defaultSuffix} {defaultFilters}" 
        return self.createQueryFromCollection(cat, date)

    def detectGameInTweet(self, tweet, resultDict): 
        """
        Searches a tweet/string for any games it may mention.
        """
        tweet = tweet.lower()
        for game, keywordList in self.queryToKeywordDict.items():
            found = False
            for keyword in keywordList:
                if keyword in tweet:
                    found = True
                    break
            resultDict[game].append(found)
        return

    def seperateGameKeys(self, keys):
        """
        Helper function transforming the game keys into data usable in other applications.
        """
        keys = re.sub(r"(-\".*?\")|(-\(.*?\))|(-\w*)", "", keys) # Remove exclusions
        state = [i[1:-1] for i in re.findall(r"\".*?\"", keys)] #Find multi word query keys
        keys = re.sub(r"\".*?\"", "", keys) #Remove multi word query keys
        state2 = [key for key in re.findall(r"\w+", keys) if key != "OR"] #Find remaining query keys
        state.extend(state2)

        return state

    def createQueryFromCollection(self, key, date = None):
        """
        Creates the base for a full query by including all of the group specific terms and
        connecting them through boolean query operators.
        """
        gamesKeys = gameKeyCollection[key]
        actionKeys = actionKeyCollection[key]
        if type(actionKeys) == str:
            query = "("
            for keywords in gamesKeys.items():
                query += f"{keywords[1]} OR "
            query = query [:-4] + ") "
            query += actionKeyCollection[key]
        elif type(actionKeys) == dict:
            query = "("
            for key in gamesKeys:
                query += f"({gamesKeys[key]} {actionKeys[key]}) OR "
            query = query [:-4] + ") "
        else:
            raise Exception("Incorrect key collection for query")

        return self.createFullQuery(query, date)


    def createFullQuery(self, base: str, date = None, dateQuery = None) -> str:
        """
        Appends additional query settings to premade group specific query base.
        Thereby creating a fully functional query.
        """
        queryTimeWindow = queryTimeWindowDefault
        if date != None: queryTimeWindow = f"until:{date} since:2022-01-01"
        if dateQuery != None: queryTimeWindow = dateQuery
        
        return f"{base} {querySettingsDefault} {queryTimeWindow} {queryBlackListDefault}"
