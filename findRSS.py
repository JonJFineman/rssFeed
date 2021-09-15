# from
# https://stackoverflow.com/questions/6327146/how-to-find-rss-feed-of-a-particular-website
# 
import sys
import requests  
from bs4 import BeautifulSoup  

def get_rss_feed(website_url):
    if website_url is None:
        print("URL should not be null")
    else:
        source_code = requests.get(website_url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, 'html.parser')
        # mime type
        # application/rdf+xml
        # application/atom+xml
        # application/xml
        # text/xml
        # 
        for link in soup.find_all("link", {"type" : "application/rdf+xml"}):
            href = link.get('href')
            print("RSS feed for " + website_url + "is --> " + str(href))

        for link in soup.find_all("link", {"type" : "application/rss+xml"}):
            href = link.get('href')
            print("RSS feed for " + website_url + "is --> " + str(href))

        for link in soup.find_all("link", {"type" : "application/atom+xml"}):
            href = link.get('href')
            print("RSS feed for " + website_url + "is --> " + str(href))

        for link in soup.find_all("link", {"type" : "application/xml"}):
            href = link.get('href')
            print("RSS feed for " + website_url + "is --> " + str(href))

        for link in soup.find_all("link", {"type" : "text/xml"}):
            href = link.get('href')
            print("RSS feed for " + website_url + "is --> " + str(href))

rssURL = sys.argv[1]
#get_rss_feed("http://www.extremetech.com/")
get_rss_feed(rssURL)
