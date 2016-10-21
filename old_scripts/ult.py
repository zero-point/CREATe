## Get Game Data from Steam API

# Input: text file containing app_id and release date for all games within the proper date range (Jan 2015 - Jul 2016), count: 12296

# Output: csv file containing app_id, name, release date, genres, metacritic rating, user rating

from collections import defaultdict
from bs4 import BeautifulSoup
import time
import cookielib
import urllib2
import json
import cfscrape

def resolve_redirects(url,count):
	print "Attempts: " + str(count)
    	try:
        	return urllib2.urlopen(url).geturl()
    	except:
        	time.sleep(5);
        	return resolve_redirects(url,count)

def readFile(filename):

        with open(filename) as json_file:
            json_data = json.load(json_file)
        return json_data

def checkDate(date):
	if '2015' in date:
		OK = True
	elif '2016' in i and any(x in i for x in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']):
		OK = True
	else:
		OK = False
	return OK

def steamspy(param,printout):
	d = defaultdict(dict)
	print "Checking SteamSpy ..."
	site = 'http://steamspy.com/api.php?request=appdetails&appid='+param 						## SteamSpy scrape

	scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
	content = scraper.get(site).content # reads content
	js = json.loads(content)

	d[param]['score_rank'] = str(js['score_rank'])
	if(d[param]['score_rank']):
		printout += ", " + str(js['score_rank'])								# user score
	else:
		printout += ", None"

	site = 'https://steamspy.com/app/'+param         								

	scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
	content = scraper.get(site).content # reads content
	soup = BeautifulSoup(content, 'html.parser')

	return printout

def sanitisedName(name):
	sname = ""
	for i in name:
		try:
			sname += str(i)
		except(UnicodeEncodeError):
			print "Improper Character: " + i

	return sname

def steamdb(param):
	site = 'https://steamdb.info/app/'+param         								## Steam DB
	print "Checking SteamDB ..."

	scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
	content = scraper.get(site).content # reads content
	soup = BeautifulSoup(content, 'html.parser')
	soup = soup.find("td", {"data-cc" : "uk"}).next_sibling.next_sibling
	results = soup.get_text()
	price_str = results.split(" ",1)[0]	# current price
	if('N/A' not in price_str):
		price = float(price_str[1:])
	else:	
		price = 0

	if('%' in results):
		discount_str = results.split("at ",1)[1]	# current discount
		discount = int(discount_str[1:-1])
	else:
		discount = 0 

		
	temp = soup.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling
	if(temp):
		lowest_str = temp.get_text() # lowest historical price
		lowest = float(lowest_str.split(" ",1)[0][1:])
	else:
		lowest = 0

	return price, discount, lowest

def api(param,rel,p):
	printout = ""	 												# appid
	print "AppID: " + param
	fileout = ""
	early = False
	ok = True

	print "Checking Steam ..."
	page = urllib2.urlopen(resolve_redirects('http://store.steampowered.com/api/appdetails?appids='+param,1))		## Steam API
	js = json.load(page)

	for i in js.keys():
		if(js[i]['success']==True):
			x = js[i]['data']
			if('game' in str(x['type']) and 'release_date' in x.keys() and checkDate(str(x['release_date']['date']))):
				print "Success"
				printout += param
				try:
					try:	
						printout += ", " + str(x['name']) 						# title
					except(UnicodeEncodeError):
						printout += ", " + sanitisedName(x['name'])

					date = str(x['release_date']['date'])
					printout += ", " + date[:-6] + date[-5:]						# release date
		
					if(x['genres']):
						printout += ", "
						for j in x['genres']:
							if 'Early' in j['description']:
								early = True
							else:
								printout += j['description'] + "-"	 			# genre
						printout = printout[:-1]
					else:
						printout += ", None"

					try:
						if(x['metacritic']):
							printout += ", " + str(x['metacritic']['score']) 			# avg critic
					except(KeyError):
						print 'No Metacritic Score'
						printout += ", None"
				except:
					p.write(param + '\n')


			else:
				print('Unsuitable: either not a game or outside the required date range')
				ok = False

		if(len(printout)<5):
			printout = "N/A\n\n"
		else:
			printout += "\n"
			fileout = printout
		print "Printout: " + printout
		rel.write(fileout)
	return 'done'


o = open('output.csv', 'w')
p = open('output_errors.txt','w')
with open('input.txt') as f:
    content = f.readlines()

print "Starting ...\n"
o.write("AppID, Name, Release Date, Genre, Metacritic Score, User Score, Full Price, Lowest Price\n\n")
for i in content:
	if(int(i[:6])):
		api(str(i[:6]),o,p)

print "Finished."
o.close()
