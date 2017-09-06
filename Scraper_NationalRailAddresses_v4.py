# v4.0 - As per v3.0 but list of rail stations is taken from an online list as opposed to locally saved
# Script to scrape railway station addresses & postcodes:
# 1 - Import list of rail station alphas and push to list
# 2 - Given a specific URL, parse the page and extract the station name, address & postcode
# 3 - Append details from #2 to CSV file
#
# https://medium.freecodecamp.org/how-to-scrape-websites-with-python-and-beautifulsoup-5946935d93fe
# http://www.fongva.com/questions/1705042106173930
#
# Current problem: Cannot pass list of URLs through to search
# Have tried:
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://stackoverflow.com/questions/35732464/looping-through-a-list-of-urls-for-web-scraping-with-beautifulsoup
# https://stackoverflow.com/questions/14512386/scraping-text-using-url-from-list-beautifulsoup4
# https://stackoverflow.com/questions/5331266/python-easiest-way-to-scrape-text-from-list-of-urls-using-beautifulsoup

#
# PART 1 - IMPORT URLs INTO ARRAY USING NUMPY & PANDAS
# Ensure that RailReferences has been extracted from naptan.app.dft.gov.uk/DataRequest/Naptan.ashx?format=csv, and an approrpiate column added for the URL
import csv
from urllib.request import urlopen
import codecs
url_stations = "http://www.nationalrail.co.uk/static/documents/content/station_codes.csv"	#Store stated url as variable 'url_stations'
csv_file = urlopen(url_stations)	# Store contents of url in variable 'csv_file'
file_output = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))	# Decode csv_file contents into utf-8 and store as variable 'file_output'
station_info = list(file_output) # Push file_output into list 'station_info'
station_alphas = [item[1] for item in station_info] # Keep 2nd item (i.e. item 1) of each sub-list and store as variable 'station_alphas'
url_head = 'http://www.nationalrail.co.uk/stations_destinations/'
url_tail = '.aspx'
station_addresses = [url_head + x + url_tail for x in station_alphas]

#
# PART 2 - PARSE HTML WITH BEAUTIFULSOUP USING LIST OF URLs
# from urllib.request import urlopen
from bs4 import BeautifulSoup
# url_station = ['http://www.nationalrail.co.uk/stations/LEW/details.html', 'http://www.nationalrail.co.uk/stations/LBG/details.html']  # specify the URL(/s)
url_station = [station_alphas[0:0]]  # specify number of items on list to use
# url_station = [url_string]  # specify the string of items to use
station_info = []
for station_page in url_station:
	page = urlopen(station_page)	# Queries website and return the html to the variable ‘page’
	soup = BeautifulSoup(page, 'html.parser')	# Parses html using beautiful soap and store in variable `soup`
	divider = soup.find('div', attrs={'class': 'c1'})	# Finds C1 divider
	station_tag = divider.find('strong')	# Finds the bold/strong tag
	station = station_tag.text.strip()	# Removes the tags leaving the required station name
	address_end = divider.text.split("station",1)[1]	# Splits the text immediately after 'station' and retains the remaining text
	address_text = address_end.split("Station facilities",1)[0]	# Splits the text immediately before 'Station facilities' and retains the preceeding text
	address_body1 = address_text.strip()
	address_body2 = address_body1.replace("                            ",", ")	# Replaces the 28 spaces at beginning of each line with an comma and space
	address_body3 = " ".join(address_body2.split())	# Concatenates entire string onto 1 line
	address_body = address_body3.replace(" , ",", ")	# Replaces the 'space & comma & space' pattern with a comma & space
	postcode = address_body[-8:]	# Identifes last 8 characters of address body
	station_info.append((station, address_body, postcode))	# Saves the data in a tuple
#
# PART 3 - EXPORT TO CSV FILE
import csv
from datetime import datetime
# open a csv file with append, so old data will not be erased
with open('RailStations.csv', 'a') as csv_file:
	writer = csv.writer(csv_file)
# The for loop
	for station, address_body, postcode in station_info:
		writer.writerow([station, address_body, postcode, datetime.now()])