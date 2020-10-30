from pytrends.request import TrendReq
from googletrans import Translator
import sys

pytrends = TrendReq(hl='en-US', tz=360)
translator = Translator()

#countries and geo codes
countries = [
    ['norway', 'NO'],
    ['switzerland', 'CH'],
    ['ireland', 'IE'],
    ['germany', 'DE'],
    ['hong_kong', 'HK'],
    ['australia', 'AU'],
    ['sweden', 'SE'],
    ['singapore', 'SG'],
    ['netherlands', 'NL'],
    ['denmark', 'DK'],
    ['finland', 'FI'],
    ['canada', 'CA'],
    ['new_zealand', 'NZ'],
    ['united_kingdom', 'GB'],
    ['united_states', 'US'],
    ['belgium', 'BE'],
    ['liechtenstein', 'LI'],
    ['japan', 'JP'],
    ['austria', 'AT'],
    ['luxembourg', 'LU'],
    ['israel', 'IL'],
    ['south_korea', 'KR'],
    ['slovenia', 'SI'],
    ['spain', 'ES'],
    ['czech_republic', 'CZ'],
    ['france', 'FR'],
    ['malta', 'MT'],
    ['italy', 'IT'],
    ['estonia', 'EE'],
    ['cyprus', 'CY'],
    ['greece', 'GR'],
    ['poland', 'PL'],
    ['lithuania', 'LT'],
    ['united_arab_emirates', 'AE'],
    ['andorra', 'AD'],
    ['saudi_arabia', 'SA'],
    ['slovakia', 'SK'],
    ['latvia', 'LV'],
    ['portugal', 'PT'],
    ['qatar', 'QA'],
    ['chile', 'CL'],
    ['brunei', 'BN'],
    ['hungary', 'HU'],
    ['bahrain', 'BH'],
    ['croatia', 'HR'],
    ['oman', 'OM'],
    ['argentina', 'AR'],
    ['russia', 'RU'],
    ['belarus', 'BY'],
    ['kazakhstan', 'KZ'],
    ['bulgaria', 'BG'],
    ['montenegro', 'ME'],
    ['romania', 'RO'],
    ['palau', 'PW'],
    ['barbados', 'BB'],
    ['kuwait', 'KW'],
    ['uruguay', 'UY'],
    ['turkey', 'TR'],
    ['bahamas', 'BS'],
    ['malaysia', 'MY'],
    ['seychelles', 'SC']
]

keywordsNumber = 0
keywords = []


def addKeyword(keyword, f):
    if keyword not in keywords:
        keywords.append(keyword)
        f.write("%s," % keyword)


with open('keywords-temp.txt', 'w') as f:
    for idx, country in enumerate(countries):
        print("")
        print("PROCESS: {:.1f}%, country: {}".format(idx*100/len(countries), country[0]))
        keywordsBase = []
        keywordsAll = []

        # trending now in selected country - 20 results
        try:
            trendingPandas = pytrends.trending_searches(pn=country[0])
            for trend in trendingPandas.values.tolist():
                keywordsBase.append(trend[0].replace(" ", ""))
        except KeyboardInterrupt:
            sys.exit()
        except:
            print("INFO: Can't get trending for country: {}".format(country[0]))

        #top charts for years 2009-2019 and country
        for year in range(2009, 2020):
            try:
                topPandas = pytrends.top_charts(year, hl='en-US', tz=300, geo=country[1])
                for trend in topPandas.values.tolist():
                    keywordsBase.append(trend[0].replace(" ", ""))
            except KeyboardInterrupt:
                sys.exit()
            except:
                print("INFO: {} year from {} country, top charts not present!".format(year, country[0]))

        #related keywords
        for keyword in keywordsBase:
            keywordsAll.append(keyword)
            try:
                relatedPandas = pytrends.suggestions(keyword=keyword)
                for trend in relatedPandas:
                    keywordsAll.append(trend['title'].replace(" ", ""))
            except KeyboardInterrupt:
                sys.exit()
            except:
                print("INFO: Can't get related keyword for {}".format(keyword))

        #translation, autodetect language
        for keyword in keywordsAll:
            try:
                result = translator.translate(keyword, dest='en')
                addKeyword(result.text.replace(" ", ""), f)
            except KeyboardInterrupt:
                sys.exit()
            except:
                addKeyword(keyword, f)
                print("INFO: Can't translate {}".format(keyword))


print("DONE: Number of keywords: {}".format(len(keywords)))