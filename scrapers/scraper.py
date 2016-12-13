from bs4 import BeautifulSoup
import re
import bottlenose
from models import Site, Subsite, Comment, Product, Mention, ProductGroup, ScrapeLog
import logging
logging.getLogger().setLevel(logging.INFO)

from session import session

class Scraper(object):

  AMAZON_MATCH_PATTERN = "(dp\/|gp\/product\/|gp\/offer\-listing\/)([a-zA-Z0-9]{10})"
  AWS_ACCESS_KEY_ID = 'AKIAIHTT6ORMUADXEIQA'
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

  def gather_threads(self):
    pass

  def find_or_create_subsite(self, url):
    pass

  def find_or_create_product_group(self, amazon_name):
    product_group = session.query(ProductGroup).filter_by(amazon_name=amazon_name).first()
    if not product_group:
      product_group = ProductGroup(amazon_name=amazon_name, name=amazon_name)
      session.add(product_group)
      session.commit()
    return product_group

  def find_or_create_comment(self, attrs):
    comment = session.query(Comment).filter_by(site_comment_ident=attrs['site_comment_ident']).first()
    if not comment:
      comment = Comment()
      for key in attrs:
        setattr(comment, key, attrs[key])
      session.add(comment)
    return comment

  def find_or_create_product(self, asin, region='US'):
    product = session.query(Product).filter_by(asin=asin).first()
    logging.info(product)
    if not product:
      attrs = self.get_product_from_amazon_api(asin, region='US')
      if attrs:
        product_group = self.find_or_create_product_group(attrs['product_group_string'])
        attrs['product_group_id'] = product_group.id
        attrs.pop('product_group_string')
        product = Product(asin=asin)
        for key in attrs:
          setattr(product, key, attrs[key])
        session.add(product)
        session.commit()
      else:
        pass
    return product

  def extract_mentions_from_text(self, attrs):
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

  def error_check(self):
    pass

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
    except: #not sure what kind of erorr
      pass

  def create_mentions(self, asin, comment_attrs):
    logging.info(comment_attrs)
    subsite = self.find_or_create_subsite(comment_attrs['subsite_name'])
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

