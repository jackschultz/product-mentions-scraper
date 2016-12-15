import requests
import json
from datetime import datetime
import re
import sys
import linecache

from bs4 import BeautifulSoup

from session import session
from models import Site, Subsite, Comment, Product, Mention, ProductGroup, ScrapeLog
from gatherer import Gatherer

import logging
logging.getLogger().setLevel(logging.INFO)
import time

headers = {"User-Agent": "Product Mentions"}
class RedditGatherer(Gatherer):

  BASE_URL = "http://www.reddit.com"
  COMMENT_URL = "https://www.reddit.com/comments/?limit=100"
  THREAD_SEARCH_URL = "https://www.reddit.com/search?q=amazon.com&sort=new&t=hour&limit=100"

  THREAD_SITE_IDENT_MATCHER = "(https|http)(:\/\/www.reddit.com\/r\/)([a-zA-Z0-9_-]*)\/(comments)\/([a-zA-Z0-9]{6})"
  COMMENT_SITE_IDENT_MATCHER = "(https|http)(:\/\/www.reddit.com\/r\/)([a-zA-Z0-9_-]*)\/(comments)\/([a-zA-Z0-9]{6})\/([a-zA-Z0-9_-]*)\/([a-zA-Z0-9]{7})"

  def comments_find_amazon_mentions_in_comments(self, comments):
    threads = []
    #now take comments, and check for amazon links
    for comment in comments:
      text = str(comment)
      matches = re.findall(self.AMAZON_MATCH_PATTERN, text)
      if matches: #meaning we found an amazon link
        permalink, sci = self.find_comment_site_ident(comment)
        comment = session.query(Comment).filter_by(site_comment_ident=sci).first()
        if not comment:
          threads.append((permalink,sci))
          logging.info(permalink)
    return threads

  def threads_find_amazon_mentions_in_text(self, posts):
    threads = []
    for post in posts:
      #check for amazon link in the text
      permalink, sti, html_string = self.find_thread_site_ident(post)
      text = str(post)
      matches = re.findall(self.AMAZON_MATCH_PATTERN, text)
      if matches:
        #if there is one, then add the link to the threads array
        #check to see if we have a comment with this already
        comment = session.query(Comment).filter_by(site_thread_ident=sti).first()
        if not comment:
          threads.append((permalink,sti))
          logging.info(permalink)
    return threads

  def comments_start_end_idents(self, scrape_log, comments):
    _, start_ident, _ = self.find_comment_site_ident(comments[-1])
    _, end_ident, _ = self.find_comment_site_ident(comments[0])
    scrape_log.start_ident = start_ident
    scrape_log.end_ident = end_ident
    return scrape_log

  def threads_start_end_idents(self, scrape_log, posts):
    _, start_ident, _ = self.find_thread_site_ident(posts[-1])
    _, end_ident, _ = self.find_thread_site_ident(posts[0])
    scrape_log.start_ident = start_ident
    scrape_log.end_ident = end_ident
    return scrape_log

  def find_comment_site_ident(self, comment):
    permalink = comment.find("a", class_="bylink")["href"]
    ident = re.match(self.COMMENT_SITE_IDENT_MATCHER, permalink).groups()[6]
    html_string = str(comment)
    return (permalink, ident, html_string)

  def find_thread_site_ident(self, post):
    permalink = post.find("a", class_="search-title")["href"].split("?")[0]
    ident = re.match(self.THREAD_SITE_IDENT_MATCHER, permalink).groups()[4]
    html_string = str(post)
    return (permalink, ident, html_string)

  def gather_text_from_threads(self, threads, data_index=0):
    for thread_url, sci in reversed(threads):
      starttime=time.time()
      self.gather_attrs_from_url(thread_url, data_index=data_index) #second on is the comment
      time.sleep(2.0 - ((time.time() - starttime) % 2.0))
    return True

  def gather_comments(self):

    scrape_log = ScrapeLog(start_time=datetime.now(), scrape_type="comment")
    session.add(scrape_log)
    session.commit() #so we can see it running on the web interface

    prev_log = session.query(ScrapeLog).filter(ScrapeLog.scrape_type=="comment").filter(ScrapeLog.end_ident != None).order_by("id desc").first()
    if prev_log:
      prev_end = prev_log.end_ident
    else:
      prev_end = 'aaaaa'
    max_page_search = 8

    try:
      comments = []
      page_count = 0
      next_comment_page_url = self.COMMENT_URL
      while True:
        response = requests.get(next_comment_page_url, headers=headers)
        result = BeautifulSoup(response.text, 'html.parser')
        found_comments = result.find_all("div", class_="comment")
        comments.extend(found_comments)
        next_comment_page_url = result.find("span", class_="next-button").find("a")["href"]
        page_count += 1
        _, last_comment_ident, _ = self.find_comment_site_ident(found_comments[-1])
        print last_comment_ident
        print prev_end
        if page_count >= max_page_search or last_comment_ident < prev_end:
          break
      scrape_log.pages_count = page_count
      scrape_log = self.comments_start_end_idents(scrape_log, comments)

      logging.info("Comment count: " + str(len(comments)))

      threads = []
      for comment in comments:
        permalink, sci, html_string = self.find_comment_site_ident(comment)
        threads.append((permalink, sci, html_string))


      logging.info("Thread count: " + str(len(threads)))

      scrape_log.comments_count = len(threads)

      start_mentions_count = session.query(Mention).count()

      self.gather_text_from_threads(threads, data_index=1)

      end_mentions_count = session.query(Mention).count()
      scrape_log.mentions_count = end_mentions_count - start_mentions_count

      success = True

    except Exception as e:
      exc_type, exc_obj, tb = sys.exc_info()
      f = tb.tb_frame
      lineno = tb.tb_lineno
      filename = f.f_code.co_filename
      linecache.checkcache(filename)
      line = linecache.getline(filename, lineno, f.f_globals)
      output = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
      logging.info(output)
      scrape_log.error = True
      scrape_log.error_message = e.message
      success = False

    scrape_log.end_time = datetime.now()
    session.add(scrape_log)
    session.commit()

    return success

  def gather_threads(self):

    scrape_log = ScrapeLog(start_time=datetime.now(), scrape_type="thread")
    session.add(scrape_log)
    session.commit()

    threads = [] #defined here in case of error
    try:
      response = requests.get(self.THREAD_SEARCH_URL, headers=headers)
      result = BeautifulSoup(response.text, 'html.parser')
      #TODO check response code
      posts = result.find_all("div", class_="search-result-link")
      scrape_log.pages_count = 1 #one page for now
      scrape_log = self.threads_start_end_idents(scrape_log, posts)

      for post in posts:
        permalink, sti, html_string = self.find_thread_site_ident(post)
        threads.append((permalink, sti, html_string))

      threads = [threads[5]]
      threads.reverse()

      scrape_log.comments_count = len(threads)
      success = True

    except Exception as e:

      scrape_log.error = True
      scrape_log.error_message = e.message
      logging.error(e)

    scrape_log.end_time = datetime.now()
    session.add(scrape_log)
    session.commit()

    print threads[0][2]
    return threads

  def gather_attrs_from_url(self, url, data_index=0):
    url = url + ".json"
    response = requests.get(url, headers=headers)
    result = response.json()
    attrs = self.gather_data_from_result(result, data_index=data_index)
    return attrs

  def gather_data_from_result(self, result, data_index=0):
    thread_data = result[0]["data"]["children"][0]["data"]
    if data_index == 1:
      comment_data = result[1]["data"]["children"][0]["data"]
      parent_attrs = self.gather_info_from_t3(thread_data)
      return self.gather_info_from_t1(comment_data, parent_attrs=parent_attrs)
    else:
      return self.gather_info_from_t3(thread_data)

  def gather_info_from_t3(self, data):
    if data["selftext"]: #empty if link elsewhere
      text = data["selftext"]
      html = data["selftext_html"]
    else:
      text = data["url"]
      html = data["url"]
    author = data["author"]
    written_at = datetime.fromtimestamp(data["created"])
    url = self.BASE_URL + data["permalink"]
    title = data["title"]
    site_thread_ident = data["name"].split("_")[-1] #form of t3_XXXXX
    site_comment_ident = site_thread_ident
    subreddit_name = data["subreddit"]
    subreddit_id = data["subreddit_id"].split("_")[-1]
    attrs = {'text': text, 'html': html, 'author': author, 'written_at': written_at, 'url': url, 'thread_title': title, 'site_thread_ident': site_thread_ident, 'site_comment_ident': site_comment_ident, 'subsite_name': subreddit_name}
    return attrs

  def gather_info_from_t1(self, data, parent_attrs={}):
    text = data["body"]
    html = data["body_html"]
    author = data["author"]
    written_at = datetime.fromtimestamp(data["created"])
    site_thread_ident =  data["link_id"].split("_")[-1]
    site_comment_ident = data["name"].split("_")[-1]
    #title, url, subreddit_name from top level
    thread_title = parent_attrs['thread_title']
    url = parent_attrs['url'] + site_comment_ident + '/'
    subsite_name = parent_attrs['subsite_name']
    attrs = {'text': text, 'html': html, 'author': author, 'written_at': written_at, 'url': url, 'thread_title': thread_title, 'site_thread_ident': site_thread_ident, 'site_comment_ident': site_comment_ident, 'subsite_name': subsite_name}
    return attrs
   # if data["replies"] != "":
   #   self.gather_info_from_listing(data["replies"])








  def gather_info_from_data(self, data):
    if data["kind"] == "Listing":
      self.gather_info_from_listing(data)
    elif data["kind"] == "t1":
      self.gather_info_from_t1(data["data"])
    elif data["kind"] == "t3":
      self.gather_info_from_t3(data["data"])

  def gather_info_from_listing(self, listing):
    for child in listing["data"]["children"]:
      self.gather_info_from_data(child)
