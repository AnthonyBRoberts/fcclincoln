import mechanize
import cookielib
import time
from datetime import date, timedelta
from bs4 import BeautifulSoup
from apps.account.models import UserProfile


def write_text_to_file(pub, text, search_term, results_file):
	for t in text:
		for child in t.children:
			if search_term in child:
				with open('../static/news-archive-search-results/temp.txt', 'w') as tempFile:
					tempFile.write("pub number: " + pub + "\n" + "search results: " + str(t) + "\n")
				with open('../static/news-archive-search-results/temp.txt', 'r') as f:
					temp = f.read()
				with open(results_file, 'r') as f2:
					temp2 = f2.read()
				with open(results_file, 'w') as results:
					results.write(temp2 + temp)


def create_results_file():
	date_string = time.strftime("%Y-%m-%d-%H-%M")
	file_location = '../static/news-archive-search-results/results' + date_string + '.txt'
	f = open(file_location, 'w')
	f.close()
	return file_location


week = timedelta(days=7)

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
for profile in UserProfile.objects.filter(user_type = 'Reporter'):        
	reporter_list.append(profile.user.email)

results_file = create_results_file()


for pub in publications:
	br.open("https://newsarchive.nebpress.com/")
	response1 = br.follow_link(text_regex=r"Guest Login")
	br.form = list(br.forms())[0]
	control1 = br.form.find_control("search_text")
	control2 = br.form.find_control("start_date")
	control3 = br.form.find_control("end_date")
	control4 = br.form.find_control("publication_filter")
	control1.value = "nns.aphillips@gmail.com"
	control2.value = "09/22/2013"
	control3.value = "09/28/2013"
	control4.value = [pub]
	response = br.submit()
	soup = BeautifulSoup(response)
	text = soup.find_all('p')
	search_term = control1.value
	write_text_to_file(pub, text, search_term, results_file)