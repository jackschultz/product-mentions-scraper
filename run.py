from scrapers.reddit_scraper import RedditScraper

def run_gather_threads():
  rs = RedditScraper()
  rs.gather_threads()

def run_gather_comments():
  rs = RedditScraper()
  rs.gather_comments()
