from __future__ import print_function
import codecs
import nltk
from nltk.corpus import stopwords
import sampleg
import re
import string
import sys
import requests
from bs4 import BeautifulSoup
import os
from googlesearch import search 
#def getURLs(query):
    
 #   return list(search(query, tld="co.in", num=10, stop=1, pause=2))
    
def getAnswers1(soup):

    '''Answers from stack overflow or stack exchange or askubuntu'''
    try:
        rs = 0
        for x in soup.find_all('div',class_ = "answercell"):
            
            if(rs == 0):
		    printthis = x.find('div',class_ = "post-text").text
		    print(printthis)
		    
		    command = "zenity --info --text "
		    command += "\""
		    command += printthis.replace("\n"," ").replace("\""," ").replace("'"," ")
		    command += "\""
		    
		    print(command)
		    k = os.system(command) 
		    
		    s1 = "zenity --question --title='Error Description' --text='Do you want to see another possible solution?'"
        		#gtk dialog
		    rs = os.system(s1)
        return (rs == 0)
			 
    except Exception as e:
        pass

def getAnswers2(soup):

    '''Answers from quora'''

    rs = 0
    try:
        for x in soup.find_all('div',class_ = "u-serif-font-main--large"):
            if(rs == 0):
		
            	printthis = x.text
            	command = "zenity --info --text "
		command += "\""
		command += printthis.replace("\n"," ").replace("\""," ").replace("'"," ")
		command += "\""
		    
	        print(command)
	        k = os.system(command) 
	 	s1 = "zenity --question --title='Error Description' --text='Do you want to see another possible solution?'"
        
		rs = os.system(s1)
        return (rs == 0)
            	
            
    except Exception as e:
        pass



def mainFunction(query):
    #listOfURLs = getURLs(query)

    q = query.replace(" ","+")
    stri = "https://www.google.co.in/search?q={}".format(q)
    mainSoup = BeautifulSoup(requests.get(stri).text,'lxml')
    listOfURLs = []
    c = 0
    for x in mainSoup.find_all('h3', class_ = 'r'):
    	
        if(x.find('a') != None):
            i = x.find('a').get('href')
        else:
            i = ""
    	print(i)    
        if(re.search("youtube",i) == None and i != ""):
            listOfURLs.append(i[7:])
        c += 1
        if(c > 15):
            break
    
    print(listOfURLs)


    for i in range(0,len(listOfURLs)):
        if(re.findall(r"https|http",listOfURLs[i]) == []):
            listOfURLs[i] = "https://" + listOfURLs[i]
    
    

    if(len(listOfURLs) > 1 and listOfURLs[0] == listOfURLs[1]):
    	del listOfURLs[0]
    print(listOfURLs)
    fl = 0
    for url in listOfURLs:
        response = requests.get(url)    #Sends a GET request.
            
        if(response.status_code == 200):
            soup = BeautifulSoup(response.text,'lxml')  # Returns a BeautifulSoup object, which represents the document as a nested data structure
            if(re.findall(r"stackoverflow|stackexchange|askubuntu",url)): 
                print("Getting answer from stack.....")
                if(getAnswers1(soup) == 0):
                	break

            elif(re.findall(r"quora",url)):
                print("Getting answer from quora....")
                if(getAnswers2(soup) == 0):
                	break

            else:
                print("Summarizing the webpage....")
                _IS_PYTHON_3 = sys.version_info.major == 3

                stop_words = stopwords.words('english')

                # The low end of shared words to consider
                LOWER_BOUND = .20

                # The high end, since anything above this is probably SEO garbage or a
                # duplicate sentence
                UPPER_BOUND = .90


                def u(s):
                
                    if _IS_PYTHON_3 or type(s) == unicode:
                        return s
                    else:
                        # not well documented but seems to work
                        return codecs.unicode_escape_decode(s)[0]


                def is_unimportant(word):
                    return word in ['.', '!', ',', ] or '\'' in word or word in stop_words


                def only_important(sent):
                    return filter(lambda w: not is_unimportant(w), sent)


                def compare_sents(sent1, sent2):
                    if not len(sent1) or not len(sent2):
                        return 0
                    return len(set(only_important(sent1)) & set(only_important(sent2))) / ((len(sent1) + len(sent2)) / 2.0)


                def compare_sents_bounded(sent1, sent2):
                    '''If the result of compare_sents is not between LOWER_BOUND and
                    UPPER_BOUND, it returns 0 instead, so outliers don't mess with the sum'''
                    cmpd = compare_sents(sent1, sent2)
                    if LOWER_BOUND < cmpd < UPPER_BOUND:
                        return cmpd
                    else:
                        return 0
                    


                def compute_score(sent, sents):
                    '''Computes the average score of sent vs the other sentences (the result of
                    sent vs itself isn't counted because it's 1, and that's above
                    UPPER_BOUND)'''
                    if not len(sent):
                        return 0
                    return sum(compare_sents_bounded(sent, sent1) for sent1 in sents) / float(len(sents))


                def summarize_block(block):
                    '''Return the sentence that best summarizes block'''
                    if not block:
                        return None
                    sents = nltk.sent_tokenize(block)
                    word_sents = list(map(nltk.word_tokenize, sents))
                    d = dict((compute_score(word_sent, word_sents), sent)
                            for sent, word_sent in zip(sents, word_sents))
                    return d[max(d.keys())]


                def find_likely_body(b):
                    '''Find the tag with the most directly-descended <p> tags'''
                    return max(b.find_all(), key=lambda t: len(t.find_all('p', recursive=False)))


                class Summary(object):

                    def __init__(self, url, article_html, title, summaries):
                        self.url = url
                        self.article_html = article_html
                        self.title = title
                        self.summaries = summaries

                    def __repr__(self):
                        return u('Summary({}, {}, {}, {})').format(repr(self.url), repr(self.article_html), repr(self.title), repr(self.summaries))

                    def __unicode__(self):
                        return u('{} - {}\n\n{}').format(self.title, self.url, '\n'.join(self.summaries))

                    def __str__(self):
                        if _IS_PYTHON_3:
                            return self.__unicode__()
                        else:
                            return self.__unicode__().encode('utf8')


                def summarize_blocks(blocks):
                    summaries = [re.sub('\s+', ' ', summarize_block(block) or '').strip()
                                for block in blocks]
                    # deduplicate and preserve order
                    summaries = sorted(set(summaries), key=summaries.index)
                    return [u(re.sub('\s+', ' ', summary.strip())) for summary in summaries if any(c.lower() in string.ascii_lowercase for c in summary)]


                def summarize_page(url):
                    import bs4
                    import requests

                    html = bs4.BeautifulSoup(requests.get(url).text,'lxml')
                    b = find_likely_body(html)
                    summaries = summarize_blocks(map(lambda p: p.text, b.find_all('p')))
                    return Summary(url, b, html.title.text if html.title else None, summaries)


                def summarize_text(text, block_sep='\n\n', url=None, title=None):
                    return Summary(url, None, title, summarize_blocks(text.split(block_sep)))

		rss = ""
		
                printthis = summarize_page(url)
                for i in printthis.summaries:
                	rss += i
                
                #rss = unicode(rss, "utf-8")
                rss = str(rss)
		command = "zenity --info --text "
		command += "\""
		command += rss.replace("\n"," ").replace("\""," ").replace("'"," ")
		command += "\""
			    
		print(command)
		if(rss != ""):
			k = os.system(command) 
                #k = os.system("zenity --info --text 'hi'") #hi should be changed to printthis
		    
		s1 = "zenity --question --title='Error Description' --text='Do you want to see another possible solution?'"
        
		rs = os.system(s1)
                if(rs != 0):
                	break    
