from scraper import OzpScraper 
from multiprocessing import Pool

if __name__ == '__main__':
    """
    Used to execute the scraper for each group seperately. General group was then called 
    through the same file based on the amount of data gathered during the scrapings shown.
    
    No longer functional due to changes on Twitter's end.
    """
    versionName = "v2"
    filePath = "data/"
    scraper = OzpScraper(versionName, filePath)
    with Pool(3) as p: #currently excluding sportsBetting cuz it doesn't work and I dunno
        print(p.map(scraper.continueQuery, ["gambling", "gacha", "lootbox"]))
    print("Scraping complete")