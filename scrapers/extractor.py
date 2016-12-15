from session import session
from models import Site, Subsite, Comment, Product, Mention, ProductGroup, ScrapeLog

import logging
logging.getLogger().setLevel(logging.INFO)

class Extractor(object):

  BASE_URL = "http://www.reddit.com" #TODO not have this in here. Bad move

  def __init__(self):
    pass

  def __str__(self):
    ""

  def find_or_create_subsite(self, subreddit_name):
    reddit = session.query(Site).filter_by(name="Reddit").first()
    subsite = session.query(Subsite).filter_by(site_id=reddit.id, name=subreddit_name).first()
    if not subsite:
      url = self.BASE_URL + "/r/" + subreddit_name
      subsite = Subsite(name=subreddit_name, site_id=reddit.id, url=url)
      session.add(subsite)
      session.commit()
    return subsite

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
