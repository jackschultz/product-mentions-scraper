from scrapers.reddit_gatherer import RedditGatherer
from scrapers.amazon_extractor import AmazonExtractor

import re
from rq import Queue
from worker import conn

q = Queue(connection=conn)

def run_gather_threads():
  rg = RedditGatherer()
  threads = rg.gather_threads()
  for thread_url, _, html_string in threads:
    q.enqueue(run_gather_attrs_from_url, thread_url, html_string, data_index=0)

def run_gather_attrs_from_url(thread_url, html_string, data_index=0):
  rg = RedditGatherer()
  #want to run the text through the matcher to see if we should waste time
  #and resources with the extraction
  matches = re.findall(AmazonExtractor.AMAZON_MATCH_PATTERN, html_string)
  if matches: #meaning we have a product
    attrs = rg.gather_attrs_from_url(thread_url, data_index=data_index)
    print attrs
    print "enququing extraction"
    q.enqueue(run_extract_mentions_from_attrs, attrs)
  else:
    print "No product matches found"

def run_extract_mentions_from_attrs(attrs):
  print "running extraction"
  ae = AmazonExtractor()
  ae.extract_mentions_from_attrs(attrs)

def run_gather_comments():
  rg = RedditGatherer()
  rg.gather_comments()

