import mechanize
import cookielib
import time
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
}
	

class Scrapper(object):

	def write_text_to_file(pub, text, search_term, results_file): 
		for t in text:
			for child in t.children:
				if search_term in child:
					with open('../static/news-archive-search-results/temp.txt', 'w') as tempFile:
						tempFile.write("\n \n pub number: " + pub + "\n" + "search results: " + str(t) + "\n \n")
					with open('../static/news-archive-search-results/temp.txt', 'r') as f:
						temp = f.read()
					with open(results_file, 'r') as f2:
						temp2 = f2.read()
					with open(results_file, 'w') as results:
						results.write(temp2 + temp)


	def create_results_file(date_info):
		date_string = time.strftime("%Y-%m-%d-%H-%M")
		file_location = '../static/news-archive-search-results/results' + date_string + '.txt'
		f = open(file_location, 'w')
		f.write(date_info)
		f.close()
		return file_location


	def get_results(start_date, end_date, date_info):

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

		reporter_list = []
		#for profile in UserProfile.objects.filter(user_type = 'Reporter'):        
			#reporter_list.append(profile.user.email)

		results_file = create_results_file(date_info)
		

		for pub in publications:
			br.open("https://newsarchive.nebpress.com/")
			response1 = br.follow_link(text_regex=r"Guest Login")
			br.form = list(br.forms())[0]
			control1 = br.form.find_control("search_text")
			control2 = br.form.find_control("start_date")
			control3 = br.form.find_control("end_date")
			control4 = br.form.find_control("publication_filter")
			control1.value = "Katie Walter"
			control2.value = start_date
			control3.value = end_date
			control4.value = [pub]
			response = br.submit()
			soup = BeautifulSoup(response)
			text = soup.find_all('p')
			search_term = control1.value
			write_text_to_file(pub, text, search_term, results_file)


	def scrape():
		week = timedelta(days=-7)
		today = datetime.today()
		end_date = today + (week*47)
		start_date = end_date + week
		stop_search_week = end_date + (week*62)
		formatted_end_date = end_date.strftime("%m/%d/%Y")
		formatted_start_date = start_date.strftime("%m/%d/%Y")
		date_info = "Results for " + formatted_start_date + " to " + formatted_end_date + ".\n \n"

		while start_date > stop_search_week:
			print start_date
			print end_date
			get_results(formatted_start_date, formatted_end_date, date_info)
			print "finished getting results for " + formatted_start_date + " to " + formatted_end_date + "."
			start_date = start_date + week
			end_date = end_date + week
			formatted_end_date = end_date.strftime("%m/%d/%Y")
			formatted_start_date = start_date.strftime("%m/%d/%Y")
			date_info = "Results for " + formatted_start_date + " to " + formatted_end_date + ".\n \n"
