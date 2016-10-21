# scrape steam api for release dates

from collections import defaultdict
#from six.moves import urllib
#import urllib.error
#import urllib.request
import time
import urllib2
import json

site= "http://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/getHistoricalData.jsp?symbol=JPASSOCIAT&fromDate=1-JAN-2012&toDate=1-AUG-2012&datePeriod=unselected&hiddDwnld=true"
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def resolve_redirects(url):
    try:
        return urllib2.urlopen(url)
    except:
#        if e.code == 429:
         time.sleep(5);
         return resolve_redirects(url)
#        raise

def readFile(filename):

        with open(filename) as json_file:
            json_data = json.load(json_file)
        return json_data

def checkDate(date):
	if '2015' in date:
		OK = True
	elif '2016' in date:
		OK = True
	else:
		OK = False
	return OK

def api(param,rel):
	info = param + " "	# appid
	info2 = ""
	d = defaultdict(dict)
	
#	page = urllib2.urlopen(resolve_redirects('http://store.steampowered.com/api/appdetails?appids='+param))		# steam api
#	js = json.load(page)



	for i in js.keys():
		if(js[i]['success']==True):
			x = js[i]['data']
			if('game' is in str(x['type']) and 'release_date' in x.keys() and checkDate(str(x['release_date']['date']))):
				info += str(x['name']) + " " # title
				for j in x['genres']:		
					if 'Early' is in j['description']:
					else:
						info += j['description'] + "-"	 # genre
				info += " "
				info += str(x['metacritic']['score']) + " " # avg critic
				info += str(x['release_date']['date']) + '\t' # release date
				info2 = info + '\n'
			else:
				info += 'none\t'

        js = json.load(resolve_redirects(urllib2.Request('http://steamspy.com/api.php?request=appdetails&appid='+param, headers=hdr)))	# steamspy api
	d[param]['score_rank'] = str(js['score_rank'])
	info += str(js['score_rank'])
	info2 = info
	
	print info
	rel.write(info2)
	return d	 


js = readFile('GetAppList.json')
rel = open('games-more.txt', 'w')
for i in js.keys():
        for j in js[i]:
                for x in js[i][j]:
                        for y in js[i][j][x]:
				api(str(y['appid']),rel)
rel.close()
