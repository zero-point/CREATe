# scrape steamspy 

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
        return urllib2.urlopen(url).geturl()
    except:
#        if e.code == 429:
         time.sleep(5);
         return resolve_redirects(url)
#        raise

def readFile(filename):

        with open(filename) as json_file:
            json_data = json.load(json_file)
        return json_data

def api(param):
	#print param
	info = ""	
	req = urllib2.Request('http://steamspy.com/api.php?request=appdetails&appid=17450', headers=hdr)
	page = urllib2.urlopen(req)
	js = json.load(page)
	for i in js.keys():
		print (i + " " + str(js[i]))
		
with open('gametitles.txt') as f:
    content = f.readlines()

#js = readFile('appid_to_name.json')

api("17450")

"""app = defaultdict(set)
for i in js.keys():
	for j in js[i]:
		for x in js[i][j]:
			for y in js[i][j][x]:
				app[y['name']] = y['appid']

out = open('gametitles_to_appid.txt', 'w')
out2 = open('all_games_info.json', 'w')
j = 1
for i in content:
	print (j)
	if(i!='\n'):
		c = i[:-1]
		if(app[str(c)]):
		#	print c
			out.write(c + ' ' + str(app[str(c)])+'\n')
			s = api(str(app[str(c)]))
			try:
				out2.write(c + '\t' + str(app[str(c)]) + '\t' + s + '\n')
			except UnicodeEncodeError:
				print ("Encoding error in title")
	j += 1
out.close()		
out2.close()"""

