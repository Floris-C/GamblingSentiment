import re

querySettingsDefault  = \
    "lang:en -filter:links" #-filter:links cuts out a lot of bots/advertisements #probably include replies TBH filter:replies, howe
queryBlackListDefault = \
    "-giveaway -crypto -cryptocasino -nft -blockchain"

gameKeyCollection= {
    "gambling": {
            "Poker": "poker",
            "Roulette": "(roulette -\"russian roulette\")",
            "Horses": "horses",
            "Craps": "(craps)",
            "Scratch Lottery": "(\"scratch card\" OR \"scratch lottery\")",
            "Sports Betting": "(football OR nba)"
            },
    "gacha": {
            "Genshin Impact": "(genshin)",
            "Raid Shadow Legends": "(raidrpg)",
            "Azur Lane": "(azur lane)",
            "Street Fighter: Duel": "(street fighter duel)",
            "Fire Emblem Heroes": "(fe heroes)",
            "Epic 7": "epic7",
            "Girl's Frontline": "(girls frontline -from:@GirlsFrontlineE)",
            "Granblue Fantasy": "(granblue -\"check out\" -\"Battle ID\")",
            "Nier Reincarnation": "(nier reincarnation)"
            },
    "lootbox": {
            "Fifa": "(fut23 OR fut22)",
            "Counter Strike": "csgo",
            "Apex Legends": "apex -predator",
            "Hearthstone": "hearthstone",
            "Clash Royale": "\"clash royale\"",
            "Magic the Gathering: Arena": "mtga"
            }, 
}

actionKeyCollection = {
    "gambling": "(gambl OR gamble OR gambling OR bet)",
    "gacha": "(pull OR roll OR gacha)",    
    "lootbox": {"Fifa": "pack or pull",
            "Counter Strike": "crate",
            "Apex Legends": "pack",
            "Hearthstone": "pack OR pull",
            "Clash Royale": "chest",
            "Magic the Gathering: Arena": "pack OR pull"
            } #"(pack OR pull OR chest OR gacha) "
}

class queryManager():  
    """ Class for creating queries using a keyword-actionword structure as well as
    for any functions which rely on that same query definition structure. """  
    def detectKeywords(content): #TODO improve this
        keywords = []
        for name, collection in gameKeyCollection.items():
            for game, keys in collection.items():
                seperatedKeys = seperateGameKeys(keys)
                for key in seperatedKeys:
                    if (re.search(r"(\W|^){}(\W|$)".format(key.lower()), content.lower()) != None) and (not game in keywords):
                    #f' {key}' in content.lower() and not (game in keywords):# TODO replace f in with proper regex cuz "apex legends" aint getting picked up
                        keywords.append(game)
        return keywords

    def seperateGameKeys(keys):
        keys = re.sub(r"(-\".*?\")|(-\w*)", "", keys) # Remove exclusions
        state = [i[1:-1] for i in re.findall(r"\".*?\"", keys)] #Find multi word query keys
        keys = re.sub(r"\".*?\"", "", keys) #Remove multi word query keys
        state2 = [key for key in re.findall(r"\w+", keys) if key != "OR"] #Find remaining query keys
        state.extend(state2)

        return state



    def createQueryFromCollection(key):
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

        defaultSuffix = "lang:en -filter:links" #-filter:links cuts out a lot of bots/advertisements #probably include replies TBH filter:replies, howe
        defaultFilters = "-giveaway -crypto -cryptocasino -nft -blockchain -eth -codes"
        return f"{query} {defaultSuffix} {defaultFilters}"


    def createFullQuery(base: str, date: Date) -> str:
        dateSuffix = date.asQuery()
        defaultSuffix = "lang:en -filter:links" #-filter:links cuts out a lot of bots/advertisements #probably include replies TBH filter:replies, howe
        defaultFilters = "-giveaway -crypto -cryptocasino -nft -blockchain -\"russian roulette\""
        return f"{base} {dateSuffix} {defaultSuffix} {defaultFilters}"
