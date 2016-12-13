import os

class Config(object):
  DEBUG = False
  TESTING = False
  DATABASE_URI = None

class ProductionConfig(Config):
  DATABASE_URI = os.environ['PMS_DATABASE_URI']

class DevelopmentConfig(Config):
  DEBUG = True
  DATABASE_URI = 'postgresql://localhost:5432/productmentions_development'

class TestingConfig(Config):
  TESTING = True
  DATABASE_URI = 'postgresql://localhost:5432/productmentions_test'
  #to run tests PMS_DATABASE_URI=postgresql://localhost:5432/productmentions_test python -m tests.scrapers.reddit_scraper_test
