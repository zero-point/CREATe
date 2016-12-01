# get all steam games from steam api games list

#from six.moves import urllib
#import urllib2
import json
#page = urllib2.urlopen('http://api.steampowered.com/ISteamApps/GetAppList/v0001/')

out = open('all_games.txt', 'w') # name id

with open('GetAppList.json', 'r') as f:
     js = json.load(f)

no_of_errors = 0
for i in js.keys():
	for j in js[i]:
		for x in js[i][j]:
			for y in js[i][j][x]:
				try:
					out.write(str(y['name']))
				except(UnicodeEncodeError):
					for i in y['name']:
						try:
							out.write(i)
						except(UnicodeEncodeError):
							print "oops"
							no_of_errors += 1
				out.write(" ")
				print y['appid']
				out.write(str(y['appid']))
				out.write('\n')

out.close()
print no_of_errors
