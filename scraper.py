from helpers.simpleDate import Date


baseQuery1 = "pull (genshin OR ffbe)"
baseQuery2 = ""
baseQuery3 = ""
baseQuery4 = ""

""" 
GACHAS
raidrpg pull lang:en -sponsored
pull (ffbe OR wotvffbe OR wotv) lang:en 

LBS

GAMBAS

"""
exampleQuery = "genshin pull -giveaway lang:en until:2022-01-02 since:2022-01-01 -filter:replies"


    
    # this fucks up the zeroes thingy.


class ScrapeSegment():
    """Scraper that """

def createQuery(base: str, date: Date) -> str:
    dateSuffix = date.asQuery()
    defaultSuffix = "lang:en -filter:replies"
    return f"{base} {dateSuffix} {defaultSuffix}"


def 