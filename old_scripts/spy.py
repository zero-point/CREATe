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

def steamspy(param,printout,p):
	d = defaultdict(dict)
	print "Checking SteamSpy ..."
	site = 'http://steamspy.com/api.php?request=appdetails&appid='+param 						## SteamSpy scrape
	try:
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
	except:
                print "ErrorSteamSpy: " + param + "\n"
		p.write("ErrorSteamSpy: " + param + "\n")

	return printout

def sanitisedName(name):
	sname = ""
	for i in name:
		try:
			sname += str(i)
		except(UnicodeEncodeError):
			print "Improper Character: " + i

	return sname

def steamdb(param,err):
	site = 'https://steamdb.info/app/'+param         								## Steam DB
	print "Checking SteamDB ..."

	price = 0
	lowest = 0
	discount = 0

	try:
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

			
		temp = soup.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling	# finding prices using soup
		if(temp):
			lowest_str = temp.get_text() # lowest historical price
			lowest = float(lowest_str.split(" ",1)[0][1:])
		else:
			lowest = 0
	except:
		print "ErrorSteamdb: " + param + "\n"
		err.write("ErrorSteamdb: " + param+"\n")

	return price, discount, lowest

def api(param,rel,p):
	printout = ""	 												# appid
	print "AppID: " + param
	fileout = ""
	ok = True

	printout += param

	if(ok):
		printout = steamspy(param, printout,p)
		price, discount, lowest = steamdb(param,p)
		printout += ", " + str(price*100/(100-price)) 								# full price
		printout += ", " + str(lowest)										# lowest price

	if(len(printout)<5):
		printout = "N/A\n\n"
	else:
		printout += "\n"
		fileout = printout
	print "Printout: " + printout
	rel.write(fileout)
	return 'done'


o = open('output.csv', 'w')		# output file	
p = open('output_errors.txt','w')	# list of appids that encountered errors (categorised as steamspy or steamdb errors)
with open('input.txt') as f:		# list of appids
    content = f.readlines()

print "Starting ...\n"
o.write("User Rating, Early Access, Full Price, Lowest Price\n\n")
for i in content:
	if(int(i[:6])):
		api(str(i[:6]),o,p)

print "Finished."
o.close()
