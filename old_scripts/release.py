# scrape steam api for release dates

from collections import defaultdict
#from six.moves import urllib
#import urllib.error
#import urllib.request
import time
import urllib2
import json

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

def checkDate(date):
	if '2015' in date:
		OK = True
	elif '2016' in date:
		OK = True
	else:
		OK = False
	return OK

def api(param,rel):
	#print param
	info = param + " "	
	info2 = ""
	page = urllib2.urlopen(resolve_redirects('http://store.steampowered.com/api/appdetails?appids='+param))
	js = json.load(page)
	for i in js.keys():
		if(js[i]['success']==True):
			try:
				if('release_date' in js[i]['data'].keys() and checkDate(str(js[i]['data']['release_date']['date']))):
					info += js[i]['data']['release_date']['date'] + '\t'
					if any(x in js[i]['data']['release_date']['date'] for x in ['Coming', 'coming', 'TBA']):
						print "dud"
					else:
						info2 = info + '\n'
				else:
					info += 'none\t'
			except(UnicodeEncodeError):
				print("Unicode Error")
	print info
	rel.write(info2)
	return info	 


js = readFile('GetAppList.json')
rel = open('games5.txt', 'w')
print "1"
for i in js.keys():
        for j in js[i]:
                for x in js[i][j]:
                        for y in js[i][j][x]:
				if(int(y['appid'])): #> 525900):  # > 471895): # > 445320): # > 409340): # 260160): #412150
					print "2"
					api(str(y['appid']),rel)
				else:
					print "End value reached"
					break;
				
rel.close()

#beg games2, games3, games4
#409360,445321, 471896 
