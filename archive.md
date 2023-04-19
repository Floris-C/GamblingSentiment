```python
def basicApproach(queryName, limit=100):
        # Retrieve Query

        # Prepare dictionary to store results
        resultDict = 


        
        # Iterate over tweets and process them
        query = createQueryFromCollection(queryName)
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i%100==0: print(f'At tweet index {i}')
            if i>=limit: break
            processTweet(tweet, resultDict)        
        
        # Save results as df/csv
        df = pd.DataFrame(resultDict)
        print(df.head())
        df.to_csv(f'{queryName}.csv')
```