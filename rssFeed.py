import feedparser
import json
import hashlib
import os.path
import sys
import datetime
import argparse
from bs4 import BeautifulSoup

from email.message import EmailMessage

import urllib.request
import smtplib

from rssConf import Conf
from reject import *



for arg in sys.argv:
    print(arg)

# get/parse arguments
parser = argparse.ArgumentParser(description='rss feed')
parser.add_argument('--env', required=False, default='DEV', help='environment DEV|TEST|PROD')
parser.add_argument('--conf', required=False, default='rss.conf', help='config file')
parser.add_argument('--homeDir', required=False, default='.', help='home dir')

args = parser.parse_args()
print(args.env, args.conf, args.homeDir)

env      = args.env
configFN = args.conf
home_dir = args.homeDir


conf = Conf(configFN)
DEBUG = conf.getItem(env, 'DEBUG')
if DEBUG == 'True':
    DEBUG = True
else:
    DEBUG = False
SEND_MAIL = conf.getItem(env, 'SEND_MAIL')
if SEND_MAIL == 'True':
    SEND_MAIL = True
else:
    SEND_MAIL = False
FROM_EMAIL_ID = conf.getItem(env, 'FROM_EMAIL_ID')
DEBUG_EMAIL_ID = conf.getItem(env, 'DEBUG_EMAIL_ID')
REJECT_EMAIL_ID = conf.getItem(env, 'REJECT_EMAIL_ID')
SUBJECT_PREFIX = conf.getItem(env, 'SUBJECT_PREFIX')
FEED = conf.getItem(env, 'FEED')
print('debug?: ', DEBUG, '\n', \
      'email?: ', SEND_MAIL, '\n', \
      'from email id: ', FROM_EMAIL_ID, '\n', \
      'debug email id: ', DEBUG_EMAIL_ID, '\n', \
      'reject id: ', REJECT_EMAIL_ID, '\n', \
      'subj pref: ', SUBJECT_PREFIX, '\n', \
      'feed: ', FEED)


with open(home_dir + '/' + FEED, 'r') as fp:
    rssList = json.load(fp)

today = datetime.date.today()

for rss in rssList['list']:
    story_list = []
    
    if rss['active'] != 'yes':
        continue
    rssURL = rss['url']
    rssName = rss['shortname']
    rssLink = rss['linktag']
    rssDesc = rss['description']
    rssEmail = rss['email']

    storiesSeen = []
    listFileName = home_dir + '/data/' + rssName + '.list'
    if os.path.isfile(listFileName) == True:
        with open(listFileName, 'r') as fd:
            storiesSeen = fd.read().splitlines()
    else:
            storiesSeen = []
                
    storySeen = False
    count = 0
    # remove geo tags from rss feeds
    req = urllib.request.Request(rssURL)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
    try:
        response = urllib.request.urlopen(req)
        response_text = response.read().decode("utf-8")
    except Exception as e:
        print('could not read: ', rssName, e)
        pass
    clean_rssURL = re.sub('<georss:point>[0-9.\- ]*</georss:point>', '', response_text)
    d = feedparser.parse(clean_rssURL)
    for story in d['entries']:
        title = story['title']
        link = story[rssLink]

        pubDate = today
        try:
            pubDate = story['published_parsed']
        except Exception as e:
            pass
        modDate = pubDate
        try:
            modDate = story['updated_parsed']
        except Exception as e:
            pass

        summary = ''
        content_value = ''
        mediaURL = ''
        messageBody = ''
        custom = False
        html = False
        try:
            # other feeds
            content = ''
            try:
                content = story['summary_detail']
            except Exception as e:
                print('could not find: ', rssName, e)
                pass
            content_value = content['value']
            messageBody += '<p>Article link:</p>'
            messageBody += '<p> <a href="' + str(link) + '">' + str(link) + '</a></p>'
            messageBody += '<p>Summary:</p>'
            messageBody += '<p>' + str(content_value) + '</p>'

            if rssName == 'ars':
                custom = True
                html = True
                content = story['content']
                content_value = content[0]['value']
                messageBody  = '<p>Article link:</p>'
                messageBody += '<p> <a href="' + str(link) + '">' + str(link) + '</a></p>'
                # @todo limit size of summary - seems like story
                messageBody += '<p>Summary:</p>'
                messageBody += '<p>' + str(content_value) + '</p>'
                # @todo add story body
                content_value = '' # dont add summary to text version

            if rssName == 'finance:the_diff':
                custom = True
                html = True
                content = story['content']
                content_value = content[0]['value']
                messageBody  = '<p>Article link:</p>'
                messageBody += '<p> <a href="' + str(link) + '">' + str(link) + '</a></p>'
                messageBody += '<p>Summary:</p>'
                messageBody += '<p>' + str(content_value) + '</p>'

            if rssName == 'hn':
                custom = True
                html = True
                content = story['summary_detail']
                content_value = content['value']

                article_tag   = 'Article URL: <a href="'
                article_tag_len = len(article_tag)
                article_start = content_value.find(article_tag) + article_tag_len
                article_stop  = content_value[article_start:].find('">') + article_start
                article_url   = content_value[article_start:article_stop]

                comment_tag   = 'Comments URL: <a href="'
                comment_tag_len = len(comment_tag)
                comment_start = content_value.find(comment_tag) + comment_tag_len
                comment_stop  = content_value[comment_start:].find('">') + comment_start
                comment_url   = content_value[comment_start:comment_stop]

                content_value  = '\nArticle: ' + article_url + '\n'
                content_value += '\nComments: ' + comment_url + '\n\n'
                messageBody  = '<p>Article link:</p>'
                messageBody += '<p> <a href="' + str(article_url) + '">' + str(article_url) + '</a></p>'
                messageBody += '<p>Comments link:</p>'
                messageBody += '<p> <a href="' + str(comment_url) + '">' + str(comment_url) + '</a></p>'
                htmlComments = ''
                textComments = ''
                try:
                    req = urllib.request.Request(comment_url)
                    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36')
                    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
                    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
                    
                    response = urllib.request.urlopen(req)
                    response_text = response.read().decode("utf-8")
                    soup = BeautifulSoup(response_text, 'html.parser')
                    i = 0
                    for comment in soup.find_all('span'):
                        c = comment.get('class')
                        if type(c) is list:
                            if c[0] == 'commtext' and c[1] == 'c00':
                                htmlComments += '<p>Comment: ' + str(i) + ' ' + '</p>'
                                htmlComments += '<p>' + str(comment.text) + '</p>'
                                textComments += 'Comment: ' + str(i) + ' '
                                textComments += str(comment.text) + '\n\n'
                                i += 1
                        if i >= 5:
                            break
                    print('hn comments found: ', i)
                except Exception as e:
                    print('could not fetch hn comments: ', e)
                    pass
                messageBody += '<p>' + htmlComments + '</p>'
                content_value += '\n\n' + textComments

            if rssName == 'npr':
                custom = True
                content = story['summary_detail']
                content_value = content['value']
                messageBody  = '<p>Article link:</p>'
                messageBody += '<p> <a href="' + str(link) + '">' + str(link) + '</a></p>'
                messageBody += '<p>Summary:</p>'
                messageBody += '<p>' + str(content_value) + '</p>'

            if rssName == 'hobby: hackaday':
                custom = True
                content = story['content']
                content_value = content[0]['value']
                messageBody  = '<p>Article link:</p>'
                messageBody += '<p> <a href="' + str(link) + '">' + str(link) + '</a></p>'
                messageBody += '<p>Summary:</p>'
                messageBody += '<p>' + str(content_value) + '</p>'

            if rssName == 'follow:ken_shirriff':
                custom = True
                link = link[0]['href']
                messageBody  = '<p>Article link:</p>'
                messageBody += '<p> <a href="' + str(link) + '">' + str(link) + '</a></p>'
                messageBody += '<p>Summary:</p>'
                messageBody += '<p>' + str(content_value) + '</p>'

            if rssName == 'follow:benson_leung':
                custom = True
                content = story['content']
                content_value = content[0]['value']
                messageBody  = '<p>Article link:</p>'
                messageBody += '<p> <a href="' + str(link) + '">' + str(link) + '</a></p>'
                messageBody += '<p>Summary:</p>'
                messageBody += '<p>' + str(content_value) + '</p>'

            if 'yt' in rssName:
                custom = True
                html = True
                mediaURL = story['media_thumbnail'][0]['url']
                messageBody  = '<p>Video link:</p>'
                messageBody += '<p> <a href="' + str(link) + '">' + '<img src="' + str(mediaURL) + '"></p>'
                messageBody += '<p>Summary:</p>'
                messageBody += '<p>' + str(content_value) + '</p>'
                # @todo need to clean up html summary. just one blob of a link, no formating
        except Exception as e:
            print('error parsing : ', rssName, e)
            pass
        #summary = content_value
        soup = BeautifulSoup(content_value, features='html.parser')
        summary = soup.get_text('\n')
        summary = str(summary)[0:512]
        if not custom:
            messageBody  = '<p>Article link:</p>'
            messageBody += '<p> <a href="' + str(link) + '">' + str(link) + '</a></p>'
            messageBody += '<p>Summary:</p>'
            messageBody += '<p>' + str(content_value) + '</p>'



        hashID = []
        if 'hobby: se_' in rssName:
            hashID.append(hashlib.md5(str(title).encode(encoding='utf_8', errors='strict')).hexdigest())
            hashID.append(hashlib.md5(str(link).encode(encoding='utf_8', errors='strict')).hexdigest())
        elif 'npr' in rssName:
            hashID.append(hashlib.md5(str(title).encode(encoding='utf_8', errors='strict')).hexdigest() + ' t')
            hashID.append(hashlib.md5(str(link).encode(encoding='utf_8', errors='strict')).hexdigest() + ' l')
        elif 'solene' in rssName:
            hashID.append(hashlib.md5( str(str(modDate) + str(title) + str(link)).encode(encoding='utf_8', errors='strict') ).hexdigest())
        elif 'follow:' in rssName:
            hashID.append(hashlib.md5(str(title).encode(encoding='utf_8', errors='strict')).hexdigest())
        else:
            hashID.append(hashlib.md5(str(title).encode(encoding='utf_8', errors='strict')).hexdigest())
            hashID.append(hashlib.md5(str(link).encode(encoding='utf_8', errors='strict')).hexdigest())

        hashSeen = False
        for h in hashID:
            if h in storiesSeen:
                hashSeen = True
        if hashSeen == True and DEBUG == False:
            continue


        count += 1
        storySeen = True
        #print(story)
        if count == 1:
            runTime = str(datetime.datetime.now())
            storiesSeen.append(str('# ' + runTime))
            print('run time: ', runTime)
        for h in hashID:
            storiesSeen.append(h)
        print('new story: ', rssName, title, link, hashID, pubDate)
        
        # get body of story for email
        messageText  = ''
        messageText += '\n' + str(link) + '\n'
        messageText += '\n' + summary + '\n\n'

        messageHTML  = '<html><head></head>'
        messageHTML += '<body>'
        messageHTML += '<p></p>'
        messageHTML += '<p></p> <p></p>'
        messageHTML += '<p></p>'
        messageHTML += messageBody
        messageHTML += '<p></p>'
        messageHTML += '<p></p> <p></p>'
        #messageHTML += '<p>' + title + '</p>'
        #messageHTML += '<p>' + 'pub date: ' + str(pubDate) + '</p>'
        #messageHTML += '<p>' + 'mod date: ' + str(modDate) + '</p>'
        #messageHTML += '<p>' + " ".join(str(i) for i in hashID) + '</p>'
        #messageHTML += '<p>' + link + '</p>'
        #messageHTML += '<p><a href="' + str(link) + '">' + str(link) + '</a></p>'
        messageHTML += '</body>'
        messageHTML += '</html>'
        #print('**** html msg:\n', messageHTML)

        #
        # see if story should be rejected
        #
        tempEmail = rssEmail
        rc = rejectSubject(rssName, title)
        if rc:
            print('*** rejecting: ', title)
            tempEmail = REJECT_EMAIL_ID

        # email story
        emailFrom = FROM_EMAIL_ID
        subject = SUBJECT_PREFIX + rssName + ': ' + title
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = emailFrom
        #emailTo = rssEmail
        emailTo = tempEmail
        if DEBUG:
            emailTo = rssEmail = DEBUG_EMAIL_ID
        msg['To'] = emailTo
        print('sending to: ', msg['To'])
        msg.set_content(messageText)
        if html:
            msg.add_alternative(messageHTML, subtype='html')

        #print(link, 'len: ', len(message))
        try:
            #print('emailing: ', rssName, title, link, hashID, pubDate)
            s = smtplib.SMTP('localhost')
            if SEND_MAIL:
                s.sendmail(emailFrom, emailTo, msg.as_string())
            s.close()
        except Exception as e:
            print(e)
            print(link, 'len text/html: ', len(messageText), len(messageHTML))
            continue

        # just use first story if debugging
        if DEBUG and count >= 1:
            break


    if storySeen == True:
        fd = open(listFileName, 'w')
        for story in storiesSeen:
            fd.write(story + '\n')
        fd.close()    
    #print(story_list)
    print('rssName: ', rssName, 'count: ', count, '\n')



print('done')
