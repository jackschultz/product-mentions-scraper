import requests
import json
from datetime import datetime
import re
import sys
import linecache
import os

from bs4 import BeautifulSoup

from session import session
from models import Site, Subsite, Comment, Product, Mention, ProductGroup, ScrapeLog
from gatherer import Gatherer

import logging
logging.getLogger().setLevel(logging.INFO)
import time

headers = {"User-Agent": "Product Mentions"}
class HackerNewsGatherer(Gatherer):

  BASE_URL = "https://hacker-news.firebaseio.com/v0/"
  MAX_ITEM_URL = BASE_URL + "maxitem.json"
  ITEM_URL = BASE_URL + "item/%s.json"

  def gather_comments(self):
    '''
      For each comment id that we're going for, return the json
    '''
    comment_data = []
    #figure out which ids we want to gather
    for comment_id in comment_ids:
      comment_data.append(self.gather_comment(comment_id))
    return comment_data

  def gather_comment(self, comment_id):
    comment_url = self.ITEM_URL % (comment_id)
    return self.gather_attrs_from_url(comment_url)

  def gather_attrs_from_url(self, url):
    response = self.get_url_with_retries(url)
    json_data = json.loads(response.text)
    return json_data

  def current_max_comment_id(self):
    response = self.get_url_with_retries(self.MAX_ITEM_URL)
    return int(response.text)
