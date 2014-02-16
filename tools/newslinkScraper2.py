import mechanize
import cookielib
import time
import json
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
#from account.models import UserProfile


NNS_clients = {
	"791": "AINSWORTH - STAR-JOURNAL - WEDNESDAY",
	"663": "ARAPAHOE - PUBLIC MIRROR - WEDNESDAY",
	"94": "ARLINGTON - CITIZEN - THURSDAY",
	"603": "AURORA - NEWS-REGISTER - WEDNESDAY",
	"736": "BASSETT - ROCK COUNTY LEADER - WEDNESDAY",
	"648": "BENKELMAN - POST & NEWS-CHRONICLE - WEDNESDAY",
	"243": "BLAIR - ENTERPRISE - FRIDAY",
	"642": "BLAIR - PILOT-TRIBUNE - TUESDAY",
	"586": "BRIDGEPORT - NEWS-BLADE - WEDNESDAY",
	"163": "BROKEN BOW - CUSTER CO. CHIEF - THURSDAY",
	"145": "CALLAWAY - COURIER - THURSDAY",
	"113": "CRAWFORD - CLIPPER - WEDNESDAY",
	"36": "DAVID CITY - BANNER-PRESS - THURSDAY",
	"727": "ELGIN - REVIEW - WEDNESDAY",
	"211": "ELKHORN - DOUGLAS CO. POST-GAZETTE - TUESDAY",
	"51": "ELWOOD - BULLETIN - WEDNESDAY",
	"418": "FAIRBURY - JOURNAL-NEWS - WEDNESDAY",
	"747": "FRIEND - SENTINEL - WEDNESDAY",
	"453": "GENOA - LEADER-TIMES - WEDNESDAY",
	"841": "GOTHENBURG - TIMES - WEDNESDAY",
	"894": "GRANT - TRIBUNE-SENTINEL - THURSDAY",
	"322": "GRETNA - GUIDE-NEWS - WEDNESDAY",
	"855": "HAYES CENT - TIMES-REPUBLICAN - THURSDAY",
	"419": "HEBRON - JOURNAL-REGISTER - WEDNESDAY",
	"710": "IMPERIAL - REPUBLICAN - THURSDAY",
	"922": "KIMBALL - WESTERN NE. OBSERVER - THURSDAY",
	"492": "LYONS  - MIRROR-SUN - THURSDAY",
	"844": "MILFORD - TIMES - WEDNESDAY",
	"985": "NELSON - NUCKOLLS CO LOCOMOTIVE GAZETTE - THURSDAY",
	"225": "NORTH BEND - EAGLE - WEDNESDAY",
	"386": "OAKLAND - INDEPENDENT - THURSDAY ",
	"675": "ORD - QUIZ - WEDNESDAY",
	"713": "PAWNEE  - REPUBLICAN - THURSDAY",
	"570": "PLAINVIEW - NEWS - WEDNESDAY",
	"573": "RAVENNA - NEWS - WEDNESDAY",
	"806": "SCHUYLER - SUN - THURSDAY",
	"754": "SEWARD - SEWARD CO. INDEPENDENT - WEDNESDAY",
	"350": "SPRINGVIEW - HERALD - WEDNESDAY",
	"261": "SUPERIOR - EXPRESS - THURSDAY",
	"85": "TECUMSEH - CHIEFTAIN - THURSDAY",
	"57": "TEKAMAH - BURT CO. PLAINDEALER - WEDNESDAY",
	"103": "TILDEN - CITIZEN NEWS - WEDNESDAY",
	"368": "TRENTON - HITCHCOCK CO. NEWS - THURSDAY",
	"479": "VALENTINE - MIDLAND NEWS - WEDNESDAY",
	"228": "VERDIGRE - EAGLE - THURSDAY",
	"48": "WAUNETA - BREEZE - THURSDAY",
	"353": "WAYNE - HERALD - THURSDAY",
	"579": "WEST POINT - NEWS - WEDNESDAY",
	"718": "WILBER - REPUBLICAN - WEDNESDAY",
	"836": "THEDFORD - THOMAS CO. HERALD - THURSDAY"
}

NNS_client_location_data = {
	"791": [-99.859022,42.547421],
	"663": [-99.899839,40.303959],
	"94":  [-96.357246,41.454244],
	"603": [-98.003537,40.866716],
	"736": [-99.537342,42.583787],
	"648": [-101.533660,40.050615],
	"243": [-96.134383,41.545562],
	"642": [-96.134383,41.545562],
	"586": [-103.098787,41.667643],
	"163": [-99.641312,41.404768],
	"145": [-99.923179,41.291348],
	"113": [-103.412297,42.683617],
	"727": [-98.081696,41.983744],
	"211": [-96.239294,41.278642],
	"51":  [-99.860603,40.588632],
	"418": [-97.177545,40.140917],
	"747": [-97.285731,40.652095],
	"453": [-97.732455,41.447638],
	"841": [-100.159381,40.931560],
	"894": [-101.726109,40.844405],
	"322": [-96.244947,41.138898],
	"855": [-101.020422,40.511278],
	"419": [-97.586574,40.168345],
	"710": [-101.642491,40.518398],
	"922": [-103.659463,41.233693],
	"492": [-96.472255,41.936110],
	"844": [-97.052311,40.772010],
	"985": [-98.066750,40.202000],
	"225": [-96.780874,41.464285],
	"386": [-96.466075,41.835133],
	"675": [-98.929962,41.602553],
	"713": [-96.153553,40.110603],
	"570": [-97.787239,42.352729],
	"573": [-98.913347,41.027700],
	"806": [-97.060195,41.448916],
	"754": [-97.096972,40.911216],
	"350": [-99.748055,42.823639],
	"261": [-98.067010,40.022415],
	"85":  [-96.191639,40.370061],
	"57":  [-96.222546,41.778008],
	"103": [-97.833599,42.045297],
	"368": [-101.013723,40.176241],
	"479": [-100.550308,42.873686],
	"228": [-98.034118,42.596437],
	"48":  [-101.372019,40.417072],
	"353": [-97.017019,42.235990],
	"579": [-96.711406,41.839635],
	"718": [-96.962376,40.481838],
	"36":  [-97.126457,41.254543],
	"836": [-100.5750,41.9789] 
}

def replace_pub_number_with_client_name(text, client_dict):

    for i, j in client_dict.iteritems():
        text = text.replace(i, j)
    return text

def get_client_location(text, location_dict):

    for i, j in location_dict.iteritems():
    	if text ==  i:
   			return j

def create_json_file():
	json_data = {"type": "FeatureCollection", "features": []}
	date_string = time.strftime("%Y-%m-%d-%H-%M")
	file_location = '../static/news-archive-search-results/results' + date_string + '.json'
	f = open(file_location, 'w')
	f.write(json.dumps(json_data))
	f.close()
	return file_location


def update_json_file(data, results_file):

	jsonFile = open(results_file, "r")
	contents = json.load(jsonFile)
	jsonFile.close()

	feature_list = contents["features"]
	feature_list.append(data)

	jsonFile = open(results_file, "w+")
	jsonFile.write(json.dumps(contents))
	jsonFile.close()


def get_results(start_date, end_date, results_jsonfile):

	# Browser
	br = mechanize.Browser()

	# Cookie Jar
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)

	# Browser options
	br.set_handle_equiv(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)

	# Follows refresh 0 but not hangs on refresh > 0
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

	# Want debugging messages?
	#br.set_debug_http(True)
	#br.set_debug_redirects(True)
	#br.set_debug_responses(True)

	# User-Agent (this is cheating, ok?)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

	br.open("https://newsarchive.nebpress.com/")
	response1 = br.follow_link(text_regex=r"Guest Login")
	br.form = list(br.forms())[0]

	control1 = br.form.find_control("search_text")
	control2 = br.form.find_control("start_date")
	control3 = br.form.find_control("end_date")
	control4 = br.form.find_control("publication_filter")

	publications = []
	for item in control4.items:
		if not item.name == "all":
			publications.append(item.name)

	reporter_list = ["Katie Walter", "Amanda Woita", "Benjamin Welch"]

	for reporter in reporter_list:
		for pub in publications:
			br.open("https://newsarchive.nebpress.com/")
			response1 = br.follow_link(text_regex=r"Guest Login")
			br.form = list(br.forms())[0]
			control1 = br.form.find_control("search_text")
			control2 = br.form.find_control("start_date")
			control3 = br.form.find_control("end_date")
			control4 = br.form.find_control("publication_filter")
			control1.value = reporter
			control2.value = start_date
			control3.value = end_date
			control4.value = [pub]
			response = br.submit()
			soup = BeautifulSoup(response)
			text = soup.find_all('p')
			for t in text:
				for child in t.children:
					if reporter in child:
						client_location = get_client_location(pub, NNS_client_location_data)
						if client_location != None:
							data = {
									"type": "Feature",  
									"properties": { "name": "", "text": "", "reporter": "", "date": "" }, 
									"geometry": { "type": "Point", "coordinates": [] }, 
									"id": "" 
									}

							client_name = replace_pub_number_with_client_name(pub, NNS_clients)
							client_property = data["properties"]
							client_property["name"] = client_name
							client_property["text"] = str(t)
							client_property["reporter"] = reporter
							client_property["date"] = start_date

							
							location_property = data["geometry"]
							location_property["coordinates"] = client_location

							data["id"] = id_counter
							
							print "Found " + client_name + " with article that includes " + reporter + " in the text."

							update_json_file(data, results_jsonfile)
							global id_counter
							id_counter += 1
						else:
							pass


week = timedelta(days=-7)
day = timedelta(days=-1)
today = datetime.today()
end_date = today + (week*50)
start_date = end_date + week - day
stop_search_week = today + (week*67)
formatted_end_date = end_date.strftime("%m/%d/%Y")
formatted_start_date = start_date.strftime("%m/%d/%Y")
date_info = "Results for " + formatted_start_date + " to " + formatted_end_date + ".\n \n"
id_counter = 1
results_jsonfile = create_json_file()


while start_date > stop_search_week:
	print formatted_start_date
	print formatted_end_date
	results = get_results(formatted_start_date, formatted_end_date, results_jsonfile)
	print "finished getting results for " + formatted_start_date + " to " + formatted_end_date + "."
	start_date = start_date + week
	end_date = end_date + week
	formatted_end_date = end_date.strftime("%m/%d/%Y")
	formatted_start_date = start_date.strftime("%m/%d/%Y")
	
