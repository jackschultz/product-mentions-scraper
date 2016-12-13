from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

Base = declarative_base()

class Site(Base):
  __tablename__ = 'sites'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  url = Column(String)
  created_at = Column(DateTime, default=datetime.now)
  updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
  subsites = relationship("Subsite", backref="site")

  def __repr__(self):
    return "<Site(name='%s', url='%s')>" % (self.name, self.url)

class Subsite(Base):
  __tablename__ = 'subsites'

  id = Column(Integer, primary_key=True)
  site_id = Column(Integer, ForeignKey('sites.id'))
  name = Column(String)
  url = Column(String)
  created_at = Column(DateTime, default=datetime.now)
  updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

  def __repr__(self):
    return "<Subsite(name='%s', url='%s')>" % (self.name, self.url)

class Comment(Base):
  __tablename__ = 'comments'

  id = Column(Integer, primary_key=True)
  subsite_id = Column(Integer, ForeignKey('subsites.id'))
  url = Column(String)
  text = Column(Text)
  author = Column(String)
  written_at = Column(DateTime)
  created_at = Column(DateTime, default=datetime.now)
  updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
  site_comment_ident = Column(String)
  site_thread_ident = Column(String)
  html = Column(Text)
  thread_title = Column(String)

  def __repr__(self):
    return "<Comment(id='%s', url='%s')>" % (self.id, self.url.encode("utf8"))

class Product(Base):
  __tablename__ = 'products'

  id = Column(Integer, primary_key=True)
  asin = Column(String)
  title = Column(String)
  product_group_id = Column(Integer, ForeignKey('product_groups.id'))
  url = Column(String)
  created_at = Column(DateTime, default=datetime.now)
  updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
  image_url = Column(String)

  def __repr__(self):
      return "<Product(id='{0}', asin='{1}', title='{2}')>".format(self.id, self.asin, self.title.encode("utf8"))

class ProductGroup(Base):
  __tablename__ = 'product_groups'

  id = Column(Integer, primary_key=True)
  amazon_name = Column(String)
  name = Column(String)
  created_at = Column(DateTime, default=datetime.now)
  updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
  products = relationship("Product")

  def __repr__(self):
    return "<ProductGroup(name='%s', amazon_name='%s')>" % (self.name, self.amazon_name)

class Mention(Base):
  __tablename__ = 'mentions'

  id = Column(Integer, primary_key=True)
  product_id = Column(Integer, ForeignKey('products.id'))
  comment_id = Column(Integer, ForeignKey('comments.id'))
  created_at = Column(DateTime, default=datetime.now)
  updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

  def __repr__(self):
    return "<Mention(product_id='%s', comment_id='%s')>" % (self.product_id, self.comment_id)

class ScrapeLog(Base):
  __tablename__ = 'scrape_logs'

  id = Column(Integer, primary_key=True)
  scrape_type = Column(String)
  start_time = Column(DateTime, default=datetime.now)
  end_time = Column(DateTime)
  start_ident = Column(String)
  end_ident = Column(String)
  mentions_count = Column(Integer)
  comments_count = Column(Integer)
  pages_count = Column(Integer)
  error = Column(Boolean)
  error_message = Column(String)
  created_at = Column(DateTime, default=datetime.now)
  updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

  def __repr__(self):
      return "<ScrapeLog(start_time='%s', end_time='%s', start_ident='%s', end_ident='%s')>" % (self.start_time, self.end_time, self.start_ident, self.end_ident)
