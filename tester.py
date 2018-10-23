from run import run_gather_reddit_threads, run_gather_reddit_comments, run_gather_hacker_news_comments
from scrapers.hacker_news_gatherer import HackerNewsGatherer
from scrapers.amazon_extractor import AmazonExtractor


hng = HackerNewsGatherer()
ae = AmazonExtractor()

max_comment_id = hng.current_max_comment_id()

comment_ids = range(max_comment_id - 100, max_comment_id)

for comment_id in comment_ids:
  attrs = hng.gather_comment(comment_id)
  if 'title' in attrs:
    #post in itself
    continue #or check if the url is an amazon url I suppose
  else:
    #this is the comment we looking for
    html_string = attrs['text'] #sometimes None if the id is a submission
    print "HN Comment ID = %s" % (comment_id)
    print html_string
    if html_string and ae.check_possible_match(html_string):
      print "WE HAVE ASINS"
      asins = ae.extract_mentions_from_attrs(attrs)
      for asin in asins:
        print "WE HAVE ASIN: %s" % (asin)

