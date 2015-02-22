#!/usr/bin/python

#==========#
#   TODO   #
#==========#
# 1. When hitting a google search result, find links on page and add to url list
# 2. Utilize the url list as an alternative deception method
# 3. Put levels of logging in


#=============#
#   Imports   #
#=============#
import httplib #for debug levels
import urllib2 #for calling other websites
import urlparse #for parsing URLs
import random #for all sorts of random things
import time #for sleeping
import re #for regular expressions (regex)


#===============#
#   constants   #
#===============#
WORD_LIST_FILENAME = "./wordlist.txt"
URL_LIST_FILENAME = "./urllist.txt"
DEBUG_MODE = True
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0"
MAX_WORDS = 1000
ALERTING = False #toggle alerting on/off
SKIPPED_EXTENSIONS = ['.pdf',]

#====================#
#   Custom Methods   #
#====================#
def alert(message):
	""" prints the message if alerting is turned on """
	if(ALERTING):
		print message
def hitURL(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent',USER_AGENT)
	opener = urllib2.build_opener()
	
	#skip pdf files
	if(url[-4:] in SKIPPED_EXTENSIONS):
		print "Skipping %s..." % (url)
		return None
	
	
	try:
		response = opener.open(request)
	except urllib2.HTTPError, e:
		print "ERRORED ON: %s" % (url)
		print str(e)
		response = None
	except Exception, e:
		print "EXCEPTED WITH: %s" % (url)
		print str(e)
		response = None
	return response

def getWordList():
	""" loads the initial list of words """

	wordFile = open(WORD_LIST_FILENAME)
	words = []
	for word in wordFile.readlines():
		word = word.strip()
		if(word not in words):
			words.append(word)
	wordFile.close()
	return words

def saveWordList(words):
	""" saves the current list of words """
	
	print "Saving word list..."
	
	wordFile = open(WORD_LIST_FILENAME,'w') #open for writing
	for word in words:
		wordFile.write(word + '\n')
	wordFile.close()

def getURLList():
	""" loads the initial list of URLs """
	
	urlFile = open(URL_LIST_FILENAME)
	urls = []
	for url in urlFile.readlines():
		url = url.strip()
		if(url not in urls):
			urls.append(url)
	urlFile.close()
	return urls

def saveURLList(urls):
	""" saves the current list of URLs """
	
	print "Saving url list..."
	
	urlFile = open(URL_LIST_FILENAME,'w') #open for writing
	for url in urls:
		urlFile.write(url + '\n')
	urlFile.close()

def downloadAllResources(link,html):
	""" downloads all of the resources on a page """

	#get all of the resources in the HTML
	imageSrcRegexPattern = """src=[\""\']([^\""\']+)"""
	compiledPattern = re.compile(imageSrcRegexPattern)
	results = compiledPattern.findall(html)
	alert("Matched '%s'" % (results))

	#get domain name of link
	urlComponents = urlparse.urlparse(link)
	domainName = "%s://%s" % (urlComponents.scheme,urlComponents.netloc)
	
	#loop through each of the resources and download it
	for resource in results:
		if(resource[:4].lower() != "http"):
			if(resource[:1] != '/'):
				resource = "%s/%s" % (domainName,resource)
			else:
				resource = "%s%s" % (domainName,resource)
		response = hitURL(resource)
		if(response):
			alert("Downloaded %s" % (resource))
		else:
			alert("Failed to download %s" % (resource))
	
	return True

def scrapeSomeWords(html,words):
	""" scrapes a random number of words from the page and adds them to the word list """
	
	wordsOnPage = html.split()
	
	#filter for code
	filterCharacters = ['<','>','=','"','&','(',')','/','\\',':',';','.','#','-',',','{','}','[',']','?','+','|','_','!','^']
	goodWords = []
	for word in wordsOnPage:
		ignoreWord = False
		for character in filterCharacters:
			if(word.find(character) != -1):
				ignoreWord = True
				break
		if(not ignoreWord):
			goodWords.append(word)
	#print goodWords
	
	#select a few of the words
	if(len(goodWords) > 5):
		maxWordsToAdd = 5
	else:
		maxWordsToAdd = len(goodWords)
	try:
		wordsToAdd = random.sample(goodWords,random.choice(range(maxWordsToAdd)))
	except IndexError, e:
		print e
		print "maxWordsToAdd was %d and goodwords was %s.  Skipping words to add..." % (maxWordsToAdd,str(goodWords))
		wordsToAdd = []
	
	words.extend(wordsToAdd)
	words = list(set(words)) #removes duplicates
	print "Words to add: %s" % (str(wordsToAdd))
	
	while(len(words) > MAX_WORDS):
		words.pop(random.choice(range(len(words))))
	
	return words

def searchGoogle(words,urls):
	""" method of deception: searches google for random phrases """
	
	#options for how many words to google
	numbersOfTerms = [1,2,3,4]
	
	#get the number of terms to search for this time
	numberOfTerms = random.choice(numbersOfTerms)
	
	#get the random sampling of search terms
	if(numberOfTerms < len(words)):
		terms = random.sample(words,numberOfTerms)
	else:
		terms = words
	
	#concat them all for a single search term
	searchTerm = ""
	for term in terms:
		searchTerm += "%s+" % (term)
	print "Searching for: %s" % searchTerm.replace('+',' ')
	
	#convert spaces to +'s
	searchTerm = searchTerm.replace(' ','+')
	
	#create google url
	url = "http://www.google.com/search?q=%s&ie=utf-8&oe=utf-8&aq=t&rls=org.mozilla:en-US:official&client=firefox-a" % (searchTerm)
	
	#hit the url
	response = hitURL(url)
	skipNumbers = range(1,10)
	if(response):
		html = response.read()
		#print html
		
		#find some urls
		href = "<h3 class=\"r\"><a href=\""
		startingPoint = 0
		numberOfLinksToSkip = random.choice(skipNumbers)
		for i in range(numberOfLinksToSkip):
			startingPoint = html.find(href,startingPoint+1)
		indexOfFirstQuote = startingPoint + len(href)
		endOfLink = html.find("\"",indexOfFirstQuote)
		link = html[indexOfFirstQuote:endOfLink]
		
		#check to see if it's a real link
		if(link[0] != " "):
			#wait a random amount of time
			#print "Waiting to hit google search result..."
			meSoSleepy()
			
			#hit the link
			print "Hitting... %s" % link
			response = hitURL(link)
			if(response):
				#get the source code
				html = response.read()
				
				#download all the images and whatnot to imitate actually hitting the site
				downloadAllResources(link,html)
				
				#get some of the random words from the page
				words = scrapeSomeWords(html,words)
	
	return (words,urls)

def traverseSavedURLs(words,urls):
	""" method of deception: traverses to a random saved url """
	
	print "Traversed to a random url..."
	
	return (words,urls)

def getMethodOfDeception():
	""" returns a random method used to fake network traffic """
	
	#list of methods to fake network traffic
	methods = [searchGoogle] #,
	#           traverseSavedURLs]
	
	#pick one of the methods at random
	methodOfChoice = random.choice(methods)
	
	return methodOfChoice

def meSoSleepy():
	""" waits for a random amount of time before returning """
	
	#since random.random() returns a number between 0.0 and 1.0,
	#a multiplier is needed to make more realistic wait times
	multipliers = [1.0,
	               5.0,
	               10.0,
	               30.0,
	               100.0,
	               250.0,
	               600.0]
	
	#get the amount of time to wait
	waitTime = random.random() * random.choice(multipliers)
	
	print "Sleeping %f seconds..." % (waitTime)
	
	#actually do the waiting
	time.sleep(waitTime)
	
	return

#=================#
#   Main Method   #
#=================#
def main():
	""" main method """

	if(DEBUG_MODE):
		httplib.HTTPConnection.debuglevel = 1

	#get the initial word list
	words = getWordList()
	
	#get the initial url list
	urls = getURLList()
	
	#seed the random generator
	random.seed()
	
	#infinite loop
	try:
		while(True):
			#determine method of deception
			method = getMethodOfDeception()
			
			#call method of deception and get their modified lists
			(words,urls) = method(words,urls)
			
			#wait a random amount of time to do it all again
			meSoSleepy()
	except KeyboardInterrupt:
		""" trying to kill the process """
		print "\nShutting down..."
		pass
	
	#save the current word list
	saveWordList(words)
	
	#save the current url list
	saveURLList(urls)

	print "Heading towards the light..."

if __name__== "__main__":
	main()
