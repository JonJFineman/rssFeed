# rssFeed.py

Yet another news aggregator. Parses Atom and RSS feeds, although you
have to discover the URL yourself and any special tags you might want to
handle.

I am using Python 3.7.7 on OpenBSD 6.7 release

In addition I installed the following packges

* py3-pip 3.7 19.1.1.1


## Dependencies

* feedparser - feedparser-5.2.1
* bs4 - BeautifulSoup4-4.9.1
* argparse - argparse-1.4.0
* configparser - configparser 5.0.0


## Installation

	cd ~ # or the parrent of whereever you want to install the software
	git clone git@github.com:JonJFineman/rssFeed.git


## Usage

You will need to change the settings in the sample_rss.conf file in the root
directory. Also the character set in runRSS.sh

I provided a sample_feeds.json for you to follow. Copy it to feeds.json

	cd ~/rssFeed
	runRSS.sh


## Operation

When run it will pull all of the entries from the URL and email each one as a
story if not seen.

For keeping track of stories seen/sent I use a simple MD5 hash of the just the
title, so I don't miss articles. For some overly aggressive sites I will hash
the title URL and modify date. I keep these in a file named by the shortname
field in the json appended by .list. I don't trim these files as some sites
keep all of their stories available.

I added it to cron and run it every fifteen minutes. See crontab.txt for a sample.

Generally the email is text based but for some I chose to deliver as multi-part
mime so I didn't always have to click through to the site.
