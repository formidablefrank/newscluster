# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

from django.http import HttpResponse, JsonResponse

import urllib2
import json
import scrapy
import scrapy
from bs4 import BeautifulSoup
import time
from datetime import date, datetime
import re
from urlparse import urlparse

# Analysis variables
stopwords = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

fakes = ['classifiedtrends', 'definitelyfilipino', 'du30newsinfo',
    'extremereaders', 'filipinewsph', 'getrealphilippines', 'theguard1an',
    'kalyepinoy', 'leaknewsph', 'dutertedefender', 'mindanation',
    'netizensph', 'newsmediaph', 'newstitans', 'okd2', 'pinoyfreedomwall',
    'pinoytrending', 'altervista', 'pinoyviralissues', 'pinoyworld',
    'publictrending', 'socialnewsph', 'tahonews', 'thevolatilian',
    'thinkingpinoy', 'trendingbalita', 'trendingnewsportal', 'trendtitan',
    'adobochronicles', 'politics', 'memebuster']

def asciiencode(unicodestr):
    return unicodestr.encode('ascii', 'ignore')

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

# Create your views here.
def index(request):
    return render(request, 'index.html', {'title': 'Hackathon'})

def results(request):
    if request.method == 'POST':
        query = request.POST['query']
    [res, urls] = search_links_in_google(query.split())
    spider = BrickSetSpider(urls)
    spider.start_requests()
    print(spider.start_requests)
    articles = spider.articles
    print(articles)
    return render(request, 'results.html', {'results': res, 'title': 'Search Results'})
    # return HttpResponse('<br>'.join(search_links_in_google(['duterte', 'fake', 'news', 'law'])))

# Searches google using the keywords stored as a list of strings as query.
# Returns a list of strings containing urls to the news site.
# Some url domains [YouTube, Wikipedia] links are filtered out
def search_links_in_google(keywords = ['This', 'is', 'a', 'sample', 'query']):
    # list of urls to exclude from list of urls
    exclude_url = ['youtube.com', 'en.wikipedia.org', 'facebook.com', 'twitter.com']

    api_key = 'AIzaSyCTrMjjE3Higupi05vwCenC6SBiRs3WNik'
    custom_search_id = '014135143817107886589:97tdpkyrjl0'

    # Query by issuing a GET request to google search api
    url = 'https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}'.format(api_key, custom_search_id, '+'.join(keywords))
    request = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
    content = urllib2.urlopen(request)
    response = content.read()

    # parse json response
    parsed = json.loads(response)

    # filter out links
    results = []
    urls = []
    for item in parsed['items']:
        is_excluded = False
        for e in exclude_url:
            if item['link'].find(e) != -1:
                is_excluded = True
                break

        root = urlparse(item['link'])
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=root)
        isverified = True
        for f in fakes:
            if f in domain:
                isverified = False

        desc = ''
        img = ''
        try:
            desc = item['pagemap']['metatags'][0]['og:description']
        except Exception as e:
            pass

        try:
            img = item['pagemap']['cse_image'][0]['src']
        except Exception as e:
            pass

        if not is_excluded:
            results.append({
                'link': item['link'],
                'title': item['title'],
                'group': len(item['title']) % 3,
                'verified': isverified,
                'desc': desc,
                'image': img
            })
            urls.append(item['link'])

    results = sorted(results, key=lambda k: k['verified'])
    return results, urls

class BrickSetSpider(scrapy.Spider):
    name = 'brickset_spider'
    urls = []
    articles = []

    def __init__(self, urls):
        self.urls = urls

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        metadata = {}
        #get metadata keys and values
        META_SELECTOR = 'meta'
        for meta in response.css(META_SELECTOR):
            KEY_SELECTOR = '::attr(property)'
            VALUE_SELECTOR = '::attr(content)'
            k = meta.css(KEY_SELECTOR).extract_first()
            if k:
                k = asciiencode(k)
            v = meta.css(VALUE_SELECTOR).extract_first()
            if v:
                v = asciiencode(v)
            yield {
                'key' : k,
                'value' : v
            }
            metadata[k] = v

        #get href of hyperlinks
        links = []
        HREF_SELECTOR = 'a::attr(href)'
        for link in response.css(HREF_SELECTOR):
            url = asciiencode(link.extract())
            yield {
                'url' : url
            }
            links.append(url)

        #get plain html
        html = response.text
        soup = BeautifulSoup(html)
        data = soup.findAll(text=True)
        result = filter(visible, data)
        content = list(result)
        content = u' '.join(content)
        content = asciiencode(content)
        words = content.split()
        words = [x.lower() for x in words]

        #get date
        datepub = re.search(r'([A-Za-z]+ \d+, \d+)', content).group(1)
        try:
            datepub = datetime.strptime(datepub, '%B %d, %Y')
        except Exception as e:
            datepub = datetime.strptime(datepub, '%b %d, %Y')
        print(datepub)

        #get root domain
        src = response.url
        root = urlparse(src)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=root)
        links2 = []
        for i in links:
            if 'http' in i:
                root2 = urlparse(i)
                domain2 = '{uri.scheme}://{uri.netloc}/'.format(uri=root2)
                links2.append(domain2)

        #get headline
        headline = response.css('h1 ::text').extract_first()
        headline = asciiencode(headline).split()

        #create new instance of Article
        author = ''
        words = [i for i in words if i not in stopwords]
        art = Article(metadata, links2, words, src, domain, datepub, headline)
        print(art)
        self.articles.append(art)

    # def closed(self, reason):
    #     with open('data.pickle', 'wb') as f:
    #         pickle.dump(articles, f, pickle.HIGHEST_PROTOCOL)


class Article:
    metadata = {}
    links = []
    src = ''
    domain = ''
    datepub = date.today()
    headline = []
    words = []
    fakes = ['classifiedtrends', 'definitelyfilipino', 'du30newsinfo',
        'extremereaders', 'filipinewsph', 'getrealphilippines', 'theguard1an',
        'kalyepinoy', 'leaknewsph', 'dutertedefender', 'mindanation',
        'netizensph', 'newsmediaph', 'newstitans', 'okd2', 'pinoyfreedomwall',
        'pinoytrending', 'altervista', 'pinoyviralissues', 'pinoyworld',
        'publictrending', 'socialnewsph', 'tahonews', 'thevolatilian',
        'thinkingpinoy', 'trendingbalita', 'trendingnewsportal', 'trendtitan']

    def __init__(self, metadata, links, words, src, domain, datepub, headline):
        self.metadata = metadata
        self.links = links
        self.words = words
        self.src = src
        self.domain = domain
        self.datepub = datepub
        self.headline = headline

    def analyze(self):
        #ask if : ? ! exist in headlines
        if ':' in self.headline or '?' in self.headline or '!' in self.headline:
            print('HEADLINE - use of symbols')
        #ask if there is a capitalized word in headline
        for h in self.headline:
            if h.isupper():
                print('HEADLINE - uppercase word')
        #check if the domain belongs to a fake
        for f in self.fakes:
            if f in self.domain:
                print('DOMAIN - flagged as a fake news site')
        #check if any of the reference links is also a fake
        for f in self.fakes:
            for l in self.links:
                if f in l:
                    print('LINK - referenced link belong to a fake news site')
        if 'I' in self.words or 'i' in self.words:
            print('WORD CHOICE - use of "i" pronoun')
        print('INDIVIDUAL ANALYSIS COMPLETE')

    def __str__(self):
        return self.headline
