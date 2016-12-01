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
import requests
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
	elif '2016' in date and any(x in date for x in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']):
		OK = True
	else:
		OK = False
	return OK

def steamspy(param,printout,p):
        d = defaultdict(dict)
        print "Checking SteamSpy ..."
        site = 'http://steamspy.com/api.php?request=appdetails&appid='+param                                            ## SteamSpy scrape
        try:
                scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
                content = scraper.get(site).content # reads content
                js = json.loads(content)

                d[param]['score_rank'] = str(js['score_rank'])
                if(d[param]['score_rank']):
                        printout += ", " + str(js['score_rank'])                                                                # user score
                else:
                        printout += ", None"

                site = 'https://steamspy.com/app/'+param

                scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
                content = scraper.get(site).content # reads content
                soup = BeautifulSoup(content, 'html.parser')
        except:
                print "ErrorSteamSpy: " + param
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
def steamdb(param,printout,err):
        site = 'https://steamdb.info/app/'+param                                                                        ## Steam DB
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
                price_str = results.split(" ",1)[0]     # current price
                if('N/A' not in price_str):
                        price = float(price_str[1:])
                else:
                        price = 0

                if('%' in results):
                        discount_str = results.split("at ",1)[1]        # current discount
                        discount = int(discount_str[1:-1])
                else:
                        discount = 0


                temp = soup.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling       # finding prices using soup
                if(temp):
                        lowest_str = temp.get_text() # lowest historical price
                        lowest = float(lowest_str.split(" ",1)[0][1:])
                else:
                        lowest = 0
        except:
                print "ErrorSteamdb: " + param
                err.write("ErrorSteamdb: " + param+"\n")
	
	printout += ", " + "{0:.2f}".format(price)								# full price
	printout += ", " + "{0:.2f}".format(lowest)								# lowest price
	#print(printout)
	return printout

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
				print "Success: valid game, data accessed"
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

					printout = steamspy(param,printout,p)
					printout = steamdb(param,printout,p)

				except:
					p.write(param + '\n')


			else:
				print('Unsuitable: either not a game or outside the required date range')

		if(len(printout)<5):
			printout = "N/A\n\n"
		else:
			printout += "\n"
			fileout = printout
		print "Printout: " + printout
		rel.write(fileout)
	return 'Done'

def drm(param,out,err):
	printout = "" + param	 												
	print "AppID: " + param
	fileout = ""
	ok = True
	eula = ""
	drm = ""
	link = ""

	print "Checking Steam for DRM info ..."
        site = 'http://store.steampowered.com/app/'+param                                                                        ## Steam Web Scrape
	rep_list = ["\\t","\\n","\\r","<br>","</br>","<div>","</div>",",","[u''","[u'","u''","'']","']","\\xa0"]

        try:
		cookies = {'birthtime': '568022401'}
		scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
		content = scraper.get(site,cookies=cookies).content # reads content
		soup = BeautifulSoup(content, 'html.parser')
		date = soup.find("span", { "class" : "date" })
		if date == None:
			print("No release date\n")
			return

		if checkDate(date.contents[0]) == False:
			print("Outwith required date range\n")
			return 
		else:
			print("Within required date range")
		cs = soup.findAll("div", { "class" : "DRM_notice" })
		full = cs

		if cs == []:
			print("No DRM\n")
			printout = printout +  ", None, None, None\n"
			out.write(printout)
			return

		if len(cs)==2:
			drm = str(cs[0].contents)
			for rep in rep_list:
				if rep in drm:	
					drm = drm.replace(rep,"")
			printout += ", " + drm
			eula = str(cs[1].find("div").contents[0]).replace(",","")
			link = str(cs[1].find("a")['href'])
			printout += ", " + eula + ", " + link + "\n"
			print(printout)
			out.write(printout)
		elif len(cs)==1:
			if cs[0].find("div"):
				info = cs[0].findAll("div")
				if len(info)>1:								
					drm = str(info[0])
					for rep in rep_list:	
						drm = drm.replace(rep,"")
					eula = str(info[1].find("a").contents[0])
					link = str(info[1].find("a")['href'])
					printout += ", " + drm + ", " + eula + ", " + link + "\n"
				else:	
					drm = str(info)		
					for rep in rep_list:
						if rep in drm:	
							drm = drm.replace(rep,"")						
					printout += ", " + drm + ", None, None" + "\n"
			else:
	#			info = cs
	#			drm = str(info[0])
	#			for rep in rep_list:	
	#				drm = drm.replace(rep,"")
	#			eula = str(info[0].find("a").contents[0])
	#			link = str(info[0].find("a")['href'])
	#			printout += ", " + drm + ", " + eula + ", " + link + "\n"

				drm = str(cs[0].contents)
				for rep in rep_list:
					if rep in drm:	
						drm = drm.replace(rep,"")
				printout += ", " + drm + ", None, None" + "\n"
	#			err.write(printout+"\n")
	#			print(cs)
	#			return
			print(printout)
			out.write(printout)
		elif len(cs)>2:
			err.write(printout + "\n")
	except:
		err.write(param + '\n')
	return printout

## main

out = open('drm_output2.csv', 'w')
err = open('drm_output_err.txt','w')#_output_errors.txt','w')
with open('input.txt') as f:
    content = f.readlines()

print "Starting ...\n"
out.write("AppID, DRM, EULA, Link\n\n")

for i in content:
	if(int(i[:6])):#>317730)):
		drm(str(i[:6]),out,err)
#drm("264000",out,err)
print "Finished."
out.close()
err.close()
