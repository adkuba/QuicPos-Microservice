from pytrends.request import TrendReq
from googletrans import Translator

pytrends = TrendReq(hl='en-US', tz=360)
translator = Translator()

#countries and geo codes
countries = [
    ['norway', 'NO'],
    ['switzerland', 'CH'],
]

keywords = []

for idx, country in enumerate(countries):

    print("")
    print("PROCESS: {:.1f} %".format(idx*100/len(countries)))
    keywordsBase = []
    keywordsAll = []

    # trending now in selected country - 20 results
    trendingPandas = pytrends.trending_searches(pn=country[0])
    for trend in trendingPandas.values.tolist():
        keywordsBase.append(trend[0].replace(" ", ""))

    #top charts for years 2009-2019 and country
    for year in range(2009, 2020):
        try:
            topPandas = pytrends.top_charts(year, hl='en-US', tz=300, geo=country[1])
            for trend in topPandas.values.tolist():
                keywordsBase.append(trend[0].replace(" ", ""))
        except:
            print("INFO: {} year from {} country, top charts not present!".format(year, country[0]))

    #related keywords
    for keyword in keywordsBase:
        keywordsAll.append(keyword)
        relatedPandas = pytrends.suggestions(keyword=keyword)
        for trend in relatedPandas:
            keywordsAll.append(trend['title'].replace(" ", ""))

    #translation, autodetect language
    for keyword in keywordsAll:
        result = translator.translate(keyword, dest='en')
        keywords.append(result.text.replace(" ", ""))


print("DONE: Number of keywords: {}".format(len(keywords)))
print("SAVING...")

with open('keywords.txt', 'w') as f:
    for keyword in keywords:
        f.write("%s," % keyword)