from apscheduler.schedulers.blocking import BlockingScheduler
from scrapers.reddit_scraper import RedditScraper

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

sched = BlockingScheduler()

def gather_threads():
  rs = RedditScraper()
  rs.gather_threads()

def gather_comments():
  rs = RedditScraper()
  rs.gather_comments()

sched.add_job(gather_threads) #run immediately
sched.add_job(gather_threads, 'interval', minutes=30)
#sched.add_job(gather_comments, 'interval', minutes=1)
sched.start()
