from scrapers.reddit_gatherer import RedditGatherer
from scrapers.hacker_news_gatherer import HackerNewsGatherer
from scrapers.amazon_extractor import AmazonExtractor
from models import ScrapeLog, Comment
from session import session

from datetime import datetime

from functools import wraps

import re
from rq import Queue
from worker import conn

import sys, os

q = Queue(connection=conn)

def log_and_time(job_type):
  def log_decorator(function):
    @wraps(function)
    def log_work(*args, **kwargs):

      print "Running " + job_type
      scrape_log = ScrapeLog(start_time=datetime.now(), job_type=job_type)
      session.add(scrape_log)
      session.commit()

      try:
        log_info = function(*args, **kwargs)

        for key, val in log_info.iteritems():
          setattr(scrape_log, key, val)

      except Exception as e:
        log_info = {}
        scrape_log.error = True
        print "Error"
        print e
        print function, args, kwargs
      else:
        print "Success"

      scrape_log.end_time = datetime.now()
      session.add(scrape_log)
      session.commit()

      return log_info #returning what the decorated function returns
    return log_work
  return log_decorator #returning the decorator function


## RUNNING THE REDDIT GATHERERS

@log_and_time("reddit_threads")
def run_gather_reddit_threads():
  rg = RedditGatherer()
  ae = AmazonExtractor()
  threads = rg.gather_threads()

  pages_count = 1 #one page for now
  start_ident = rg.find_site_thread_ident(threads[0][0])
  end_ident = rg.find_site_thread_ident(threads[-1][0])

  comments_count = len(threads)
  mentions_count = 0
  for thread_url, _, html_string in threads:
    if ae.check_possible_match(html_string):
      mentions_count += 1
      q.enqueue(run_gather_reddit_attrs_from_url, thread_url, html_string, data_index=0)
      print "found match: " + thread_url
    else:
      print "no match: " + thread_url

  retval = {'pages_count': pages_count, 'start_ident': start_ident, 'end_ident': end_ident, 'comments_count': comments_count, 'mentions_count': mentions_count}
  return retval

@log_and_time("reddit_comment_base")
def run_gather_reddit_comments():
  return gather_reddit_comments_work(RedditGatherer.COMMENT_URL, 0)

@log_and_time("comment_url")
def run_gather_reddit_comments_from_url(comment_url, page_count):
  return gather_reddit_comments_work(comment_url, page_count)

def gather_reddit_comments_work(comment_url, page_count):
  max_page_count = 3

  rg = RedditGatherer()
  ae = AmazonExtractor()

  threads, next_comments_page_url = rg.gather_reddit_comments_from_url(comment_url, page_count)

  if threads:
    start_ident = rg.find_site_comment_ident(threads[0][0])
    end_ident = rg.find_site_comment_ident(threads[-1][0])

    comments_count = len(threads)
    mentions_count = 0
    for thread_url, _, html_string in threads:
      if ae.check_possible_match(html_string):
        mentions_count += 1
        q.enqueue(run_gather_reddit_attrs_from_url, thread_url, html_string, data_index=1)

    page_count += 1
    if page_count < max_page_count:
      q.enqueue(run_gather_reddit_comments_from_url, next_comments_page_url, page_count)

    retval = {'pages_count': 1, 'start_ident': start_ident, 'end_ident': end_ident, 'comments_count': comments_count, 'mentions_count': mentions_count}
  else:
    retval = {'pages_count': 1, 'start_ident': None, 'end_ident': None, 'comments_count': 0, 'mentions_count': 0, 'error_message': 'Nothing there'}
  return retval

@log_and_time("reddit_attrs")
def run_gather_reddit_attrs_from_url(thread_url, html_string, data_index=0):
  rg = RedditGatherer()

  if data_index == 0:
    ident = rg.find_site_thread_ident(thread_url)
  elif data_index == 1:
    ident = rg.find_site_comment_ident(thread_url)

  pages_count = 0
  comment = session.query(Comment).filter_by(site_comment_ident=ident).first()
  if not comment:
    #want to run the text through the matcher to see if we should waste time
    #and resources with the extraction
    attrs = rg.gather_attrs_from_url(thread_url, data_index=data_index)
    pages_count = 1
    print "enququing extraction"
    q.enqueue(run_extract_reddit_mentions_from_attrs, attrs)

  retval = {'start_ident': ident, 'pages_count': pages_count}
  return retval

@log_and_time("extract_reddit_amazon")
def run_extract_reddit_mentions_from_attrs(attrs):

  ident = attrs["site_comment_ident"]

  print "running reddit extraction"
  ae = AmazonExtractor()
  asins = ae.extract_mentions_from_attrs(attrs)
  comments_count = 1 #one url
  mentions_count = len(asins)

  retval = {'comments_count': comments_count, 'mentions_count': mentions_count, 'start_ident': ident}
  return retval


## RUNNING THE HACKER NEWS GATHERERS

@log_and_time("hacker_news_comments")
def run_gather_hacker_news_comments():
  hng = HackerNewsGatherer()
  ae = AmazonExtractor()

  comments = hng.gather_comments()
  start_id = 0
  end_id = 1

  mentions_count = 0
  comments_count = len(comments)
  for attrs in comments:
    #attrs here is the json response
    html_string = comment['text'] #sometimes None if the id is a submission
    if html_string and ae.check_possible_match(html_string):
      mentions_count += 1
      q.enqueue(run_extract_hacker_news_mentions_from_attrs, attrs)
    else:
      print "no match"

  retval = {'pages_count': pages_count, 'start_ident': start_ident, 'end_ident': end_ident, 'comments_count': comments_count, 'mentions_count': mentions_count}
  return retval

@log_and_time("extract_hacker_news_amazon")
def run_extract_hacker_news_mentions_from_attrs(attrs):

  print "running hacker news amazon extraction"
  comment_id = attrs['id']
  ae = AmazonExtractor()
  asins = ae.extract_mentions_from_attrs(attrs)
  comments_count = 1 #one url
  mentions_count = len(asins)

  retval = {'comments_count': comment_count, 'mentions_count': mentions_count, 'start_ident': comment_id}
  return retval

