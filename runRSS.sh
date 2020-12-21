set -x

LANG="en_US.UTF-8" ; export LANG
MM_CHARSET="UTF-8" ; export MM_CHARSET

#/usr/local/bin/python3 /home/jjf/src/rssFeed/rssFeed.py --env DEV --conf /home/jjf/src/rssFeed/rss.conf --homeDir /home/jjf/src/rssFeed > /home/jjf/src/rssFeed/data/cron.log 2>&1
/usr/local/bin/python3 /home/jjf/src/rssFeed/rssFeed.py --env TEST --conf /home/jjf/src/rssFeed/rss.conf --homeDir /home/jjf/src/rssFeed
