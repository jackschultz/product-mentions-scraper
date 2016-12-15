from bs4 import BeautifulSoup
import re
import bottlenose

import logging
logging.getLogger().setLevel(logging.INFO)

from session import session
from models import Site, Subsite, Comment, Product, Mention, ProductGroup, ScrapeLog
from extractor import Extractor

class AmazonExtractor(Extractor):

  AMAZON_MATCH_PATTERN = "(dp\/|gp\/product\/|gp\/offer\-listing\/)([a-zA-Z0-9]{10})"
  AWS_ACCESS_KEY_ID = 'AKIAIWJL5AW2GVB47VQA'
  AWS_SECRET_ACCESS_KEY = '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'
  AWS_ASSOCIATE_TAG = 'pmentions-20'

  REGIONS = {
      '.ca': 'CA',
      '.cn': 'CN',
      '.de': 'DE',
      '.es': 'ES',
      '.fr': 'FR',
      '.in': 'IN',
      '.it': 'IT',
      '.co.jp': 'JP',
      '.co.uk': 'UK',
      '.com': 'US',
      '.com.br': 'BR',
      '.com.mx': 'MX'
  }

  def __init__(self):
    pass

  def __str__(self):
    ""

  def extract_mentions_from_attrs(self, attrs):
    text = attrs["text"]
    asins = []
    matches = re.findall(self.AMAZON_MATCH_PATTERN, text)
    for _, asin in matches:
      asins.append(asin)
    for asin in set(asins):
      self.create_mentions(asin, attrs)

  def error_handler(self, err):
    ex = err['exception']
    if isinstance(ex, HTTPError) and ex.code == 503:
        time.sleep(random.expovariate(0.1))
        return True
    return False

  def error_check_amazon_api(self, message):
    if not message:
      return True
    invalid_value = "is not a valid value for ItemId"
    not_accessable = "This item is not accessible through the Product Advertising API"
    if invalid_value in message: #probably want to just error totally?
      return False #complete fail
    if not_accessable in message:
      return False #still know some things though
    return False

  def get_product_from_amazon_api(self, asin, region='US'):
    try:
      amazon = bottlenose.Amazon(self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY, self.AWS_ASSOCIATE_TAG, Region=region)
      response = amazon.ItemLookup(ItemId=asin, ResponseGroup="Large")
      parsed = BeautifulSoup(response, "lxml")
      logging.info(parsed.error)
      logging.info(parsed.productgroup)
      print parsed
      if self.error_check_amazon_api(parsed.error):
        title = parsed.title.text
        product_group_string = parsed.productgroup.text
        url = "https://www.amazon.com/dp/%s/" % asin
        image_url = parsed.mediumimage.url.text
        return {'title': title, 'product_group_string': product_group_string, 'url': url, 'image_url': image_url}
      else:
        logging.info("Error from Amazon" + parsed.error)
        url = "https://www.amazon.com/dp/%s/" % asin
        return {'title': '', 'product_group_string': 'Unknown', 'url': url, 'image_url': ''}
    except Exception as e:
      print "ASDF"
      print e
      print "QWER"

  def create_mentions(self, asin, comment_attrs):
    logging.info(comment_attrs)
    logging.info(asin)
    subsite = self.find_or_create_subsite(comment_attrs['subsite_name'])
    logging.info("Subsite: " + str(subsite))
    comment_attrs['subsite_id'] = subsite.id
    comment = self.find_or_create_comment(comment_attrs)
    product = self.find_or_create_product(asin)
    logging.info(comment)
    logging.info(product)
    if product and comment:
      mention = session.query(Mention).filter_by(product_id=product.id, comment_id=comment.id).first()
      if not mention:
        mention = Mention(product_id=product.id, comment_id=comment.id)
        session.add(mention)
        session.commit()

