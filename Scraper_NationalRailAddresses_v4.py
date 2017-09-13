# v4.3 - Remove 'station' suffix from station name, and ' near' prefix of town
# v4.2 - Addition of Town. Addition of counter. Pauses for 25 mins after each block of 600 to avoid being blocked. Investigate API
# v4.1 - As per v4.0 but ignores 404 errors, and appends output after each loop instead of on completion of list

# Script to scrape railway station addresses & postcodes:
# 1 - Import list of rail station alphas and push to list
# 2 - Given a specific URL, or list of URLS obtained from National Rail, parse the page and extract the station name, address, county & postcode
# 3 - Append details from #2 to CSV file
#
# Primary sources of info
# https://medium.freecodecamp.org/how-to-scrape-websites-with-python-and-beautifulsoup-5946935d93fe
# http://www.fongva.com/questions/1705042106173930
# https://stackoverflow.com/questions/12572362/get-a-string-after-a-specific-substring
# https://github.com/prabhu/pynationalrail
#
# Future versions - check NRDP KnowledgeBase API - http://nrodwiki.rockshore.net/index.php/KnowledgeBase#Accessing_the_KnowledgeBase_Feeds
#
# For Darwin enquiries:
# http://blog.redanorak.co.uk/post/110712038695/simple-python-client-for-national-rail-enquiries

# PART 1 - IMPORT URLs INTO ARRAY USING NUMPY & PANDAS
# Ensure that RailReferences has been extracted from naptan.app.dft.gov.uk/DataRequest/Naptan.ashx?format=csv, and an approrpiate column added for the URL
import csv
from urllib.request import urlopen
import codecs
station_source = "http://www.nationalrail.co.uk/static/documents/content/station_codes.csv"	#Store stated url as variable 'station_source'
csv_file = urlopen(station_source)	# Store contents of url in variable 'csv_file'
file_output = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))	# Decode csv_file contents into utf-8 and store as variable 'file_output'
station_info = list(file_output) # Push file_output into list 'station_info'
station_alphas = [item[1] for item in station_info] # Keep 2nd item (i.e. item 1) of each sub-list and store as variable 'station_alphas'
url_head = 'http://www.nationalrail.co.uk/stations/'
url_tail = '/details.html'
station_url = [url_head + x + url_tail for x in station_alphas]

# PART 2 - PARSE HTML WITH BEAUTIFULSOUP USING LIST OF URLs
from bs4 import BeautifulSoup
import re
import csv
import time
from datetime import datetime
# station_list = ['http://www.nationalrail.co.uk/stations/ASI/details.html', 'http://www.nationalrail.co.uk/stations/LBG/details.html']  # manually specify the URL(s)
station_list = station_url[1:150]  # specify number of items on list to use - start from 1, as 0 is the header
# station_list = station_url  # specify the list to use
# station_list.pop(0)		# remove 0th item, whish is header
station_info = []
counter = 0		# Start counter at zero
for station_page in station_list:
	if counter == 600 or counter == 1200 or counter == 1800 or counter == 2400 or counter == 3000 :
		time.sleep(1500)		# Every time counter hits a multiple of 600, pause for 30 mins before continuing
	try:
		page = urlopen(station_page)		# Queries website and return the html to the variable ‘page’
	except(Exception) as e:
		print(station_page)
		continue		# If urlopen resuults in an error (i.e. if link is dead), proceed to next
	soup = BeautifulSoup(page, 'html.parser')	# Parses html using beautiful soap and store in variable `soup`
	divider = soup.find('div', attrs={'class': 'c1'})	# Finds C1 divider
	station_tag = divider.find('strong')	# Finds the bold/strong tag
	station = station_tag.text.strip()	# Removes the tags leaving the required station name
	address_end = divider.text.split(station,1)[1]	# Splits the text immediately after 'station' once only (indicated by 1) and retains the text following the split, as indicated by [1]
	address_text = address_end.split("Station facilities",1)[0]	# Splits the text immediately before 'Station facilities' and retains the preceeding text
	address_body1 = address_text.strip()	# Remove leading & ending whitespace
	address_body2 = address_body1.replace("                            ",", ")	# Replaces the 28 spaces at beginning of each line with an comma and space
	address_body3 = " ".join(address_body2.split())	# Concatenates entire string onto 1 line
	address_body = address_body3.replace(" , ",", ")	# Replaces the 'space & comma & space' pattern with a comma & space
	postalcode = address_body[-8:]	# Identifes the postcode using the last 8 characters of address body and stores as postalcode
	postcode = postalcode.lstrip(',')		# Removes commas from postalcode and stores as postcode
	third_last_comma = address_body[:address_body[:address_body.rfind(",")].rfind(",")].rfind(",")+2		# Identifies the index of the antepenultimate comma	
	second_last_comma = address_body[:address_body.rfind(",")].rfind(",")+2		# Identifies the index of the penultimate comma
	last_comma = address_body.rfind(",")		# Identifies the index of the final comma
	county = address_body[second_last_comma:last_comma]		# Identifies the county using the commas as per above
	town = address_body[third_last_comma:second_last_comma-2]		# Identifies the town using the commas as per above
	station_code = station_page[39:42]		# Identifies 3 letter station code aka CRS
	station_info.append((station_code, station.replace(' station', ''), address_body.strip(), town.replace(' near', ''), county, postcode.strip()))	# Saves the data in a tuple, and also removes leading & ending whitespace from each attribute
# Create a csv file - each new record will be appended by virtue of attribute 'a'. To overwrite, use attribute 'w' and resurrect PART 3. NB - newline='' is used to avoid having an empty line between each printed record
	with open('RailStations.csv', 'a', newline='') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow([station_code, station.replace(' station', ''), address_body.strip(), town.replace(' near', ''), county, postcode.strip(), datetime.now()])		# Remove 'station' suffix from station name, and ' near' prefix of town
	counter += 1		# Increment counter by 1 before restarting For statement

# PART 3 - EXPORT TO CSV FILE
#import csv
#from datetime import datetime
# Create a csv file - existing data will be overwritten unless attribute 'a' is used instead of 'wb'. NB - newline='' is used to avoid having an empty line between each printed record
#with open('RailStations.csv', 'w', newline='') as csv_file:
#	writer = csv.writer(csv_file)
# The for loop
#	for station_code, station.station.replace(' station', ''), address_body.strip(), town.replace(' near', ''), county, postcode.strip() in station_info:
#		writer.writerow([station_code, station.station.replace(' station', ''), address_body.strip(), town.replace(' near', ''), county, postcode.strip(), datetime.now()])
