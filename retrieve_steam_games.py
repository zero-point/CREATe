from six.moves import urllib
page = urllib.request.urlopen('http://api.steampowered.com/ISteamApps/GetAppList/v0001/')

out = open('appid_to_name.json', 'w')
out.write(str(page.read()))
out.close()
