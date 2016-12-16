from scrapers.reddit_gatherer import RedditGatherer
from scrapers.amazon_extractor import AmazonExtractor
from models import ScrapeLog, Comment
from session import session

from datetime import datetime

import re
from rq import Queue
from worker import conn

q = Queue(connection=conn)


def log_and_time(job_type):
  def log(function):
    scrape_log = ScrapeLog(start_time=datetime.now(), scrape_type=job_type)
    session.add(scrape_log)
    session.commit()

    try:
      log_info = function()
    except Exception as e:
      scrape_log.error = True
      scrape_log.error_message = e.message

    scrape_log.end_time = datetime.now()
    session.add(scrape_log)
    session.commit()

    return log_info

  return log

def run_gather_threads():

  scrape_log = ScrapeLog(start_time=datetime.now(), scrape_type="thread")
  session.add(scrape_log)
  session.commit()

  try:
    rg = RedditGatherer()
    ae = AmazonExtractor()
    threads = rg.gather_threads()

    scrape_log.pages_count = 1 #one page for now
    scrape_log.start_ident = rg.find_site_thread_ident(threads[0][0])
    scrape_log.start_end = rg.find_site_thread_ident(threads[-1][0])

    comments_count = 0
    for thread_url, _, html_string in threads:
      if ae.check_possible_match(html_string):
        print thread_url
        comments_count += 1
        q.enqueue(run_gather_attrs_from_url, thread_url, html_string, data_index=0)
      else:
        print "no match"
    scrape_log.comments_count = comments_count
  except Exception as e:
    #TODO re-enqueue this job because it failed?
    scrape_log.error = True
    scrape_log.error_message = e.message

  scrape_log.end_time = datetime.now()
  session.add(scrape_log)
  session.commit()

def run_gather_comments():

  scrape_log = ScrapeLog(start_time=datetime.now(), scrape_type="comment")
  session.add(scrape_log)
  session.commit()

  try:
    rg = RedditGatherer()
    ae = AmazonExtractor()
    threads = rg.gather_comments()

    scrape_log.pages_count = 5 #all eight pages for now
    scrape_log.start_ident = rg.find_site_comment_ident(threads[0][0])
    scrape_log.start_end = rg.find_site_comment_ident(threads[-1][0])

    comments_count = 0
    for thread_url, _, html_string in threads:
      if ae.check_possible_match(html_string):
        print thread_url
        comments_count += 1
        q.enqueue(run_gather_attrs_from_url, thread_url, html_string, data_index=1)
    scrape_log.comments_count = comments_count
  except Exception as e:
    #TODO re-enqueue this job because it failed?
    scrape_log.error = True
    scrape_log.error_message = e

  scrape_log.end_time = datetime.now()
  session.add(scrape_log)
  session.commit()


def run_gather_attrs_from_url(thread_url, html_string, data_index=0):
  rg = RedditGatherer()

  if data_index == 0:
    ident = rg.find_site_thread_ident(thread_url)
  elif data_index == 1:
    ident = rg.find_site_comment_ident(thread_url)

  scrape_log = ScrapeLog(start_time=datetime.now(), scrape_type="reddit_attrs", start_ident=ident)
  session.add(scrape_log)
  session.commit()

  try:
    #check if we've seen this ident before

    comment = session.query(Comment).filter_by(site_comment_ident=ident).first()
    if not comment:
      #want to run the text through the matcher to see if we should waste time
      #and resources with the extraction
      attrs = rg.gather_attrs_from_url(thread_url, data_index=data_index)
      print "enququing extraction"
      q.enqueue(run_extract_mentions_from_attrs, attrs)
  except Exception as e:
    #TODO re-enqueue this job because it failed?
    scrape_log.error = True
    scrape_log.error_message = e.message

  scrape_log.end_time = datetime.now()
  session.add(scrape_log)
  session.commit()

def run_extract_mentions_from_attrs(attrs):

  ident = attrs["site_comment_ident"]
  scrape_log = ScrapeLog(start_time=datetime.now(), scrape_type="extract_amazon", start_ident=ident)
  session.add(scrape_log)
  session.commit()

  try:
    print "running extraction"
    ae = AmazonExtractor()
    asins = ae.extract_mentions_from_attrs(attrs)
    scrape_log.comments_count = 1 #one url
    scrape_log.mentions_count = len(asins)
  except Exception as e:
    #TODO re-enqueue this job because it failed?
    scrape_log.error = True
    scrape_log.error_message = e.message

  scrape_log.end_time = datetime.now()
  session.add(scrape_log)
  session.commit()

