import unittest
import json
from scrapers.reddit_Gathere import RedditGatherer
from models import Site, Subsite, Comment, Product, Mention, ProductGroup, ScrapeLog
from session import session
import os
from bs4 import BeautifulSoup

class TestRedditGatherer(unittest.TestCase):

  def setUp(self):
    #create subsite
    self.find_or_create_site()
    self.rs = RedditGatherer()

  def find_or_create_site(self):
    reddit = session.query(Site).filter_by(name="Reddit").first()
    if not reddit:
      reddit = Site(name="Reddit", url="https://www.reddit.com/")
      session.add(reddit)
      session.commit()

  def tearDown(self):
    pass

  def test_comment_created(self):
    session.query(Comment).delete()
    with open('tests/files/comment.json') as comment_json:
      result = json.load(comment_json)
      before_comment_count = session.query(Comment).count()
      print session.query(Comment).all()
      self.rs.gather_data_from_result(result, data_index=1)
      after_comment_count = session.query(Comment).count()
      self.assertEqual(before_comment_count+1, after_comment_count)

  def test_product_created(self):
    session.query(Product).delete()
    with open('tests/files/comment.json') as comment_json:
      result = json.load(comment_json)
      before_product_count = session.query(Product).count()
      print session.query(Product).all()
      self.rs.gather_data_from_result(result, data_index=1)
      after_product_count = session.query(Product).count()
      self.assertEqual(before_product_count+1, after_product_count)

  def test_comment_amazon_link_find(self):
    with open('tests/files/comments.html') as comments_html:
      result = BeautifulSoup(comments_html, 'html.parser')
      comments = result.find_all("div", class_="comment")
      threads = self.rs.comments_find_amazon_mentions_in_comments(comments)
      self.assertEqual(len(threads), 1)
      self.assertEqual(threads[0][0], 'https://www.reddit.com/r/AskReddit/comments/5htt6k/cops_of_reddit_whats_the_creepiest_thing_youve/db3nc6w/')
      self.assertEqual(threads[0][1], 'db3nc6w')

  def test_find_thread_site_ident(self):
    #link, ident = self.rs.find_thread_site_ident(post)
    #self.assertEqual(link, '')
    #self.assertEqual(ident, '')
    pass

  def test_find_comment_site_ident(self):
    #link, ident = self.rs.find_comment_site_ident(comment)
    #self.assertEqual(link, '')
    #self.assertEqual(ident, '')
    pass

  def test_comments_start_end_idents(self):
    #scrape_log = ScrapeLog()
    #comments = []
    #self.rs.comments_start_end_idents(scrape_log, comments)
    #start_ident = ''
    #end_ident = ''
    #self.assertEqual(start_ident, scrape_log.start_ident)
    #self.assertEqual(end_ident, scrape_log.end_ident)
    pass

  def test_threads_start_end_idents(self):
    #scrape_log = ScrapeLog()
    #posts = []
    #scrape_log = self.rs.threads_start_end_idents(scrape_log, posts)
    #start_ident = ''
    #end_ident = ''
    #self.assertEqual(start_ident, scrape_log.start_ident)
    #self.assertEqual(end_ident, scrape_log.end_ident)
    pass

  def test_threads_find_amazon_mentions_in_text(self):
    #posts = []
    #threads = self.rs.threads_find_amazon_mentions_in_text(posts)
    #self.assertEqual(len(threads), 1)
    pass

  def test_comments_find_amazon_mentions_in_comments(self):
    #comments = []
    #threads = self.rs.comments_find_amazon_mentions_in_comments(comments)
    #self.assertEqual(len(threads), 1)
    pass

if __name__ == '__main__':
    unittest.main()
