import os

from models import ScrapeLog
from session import session
from scrapers.reddit_scraper import RedditScraper

from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def home():
  logs = session.query(ScrapeLog).order_by("id desc").all()
  return render_template('home.html', logs=logs)

@app.route("/threads")
def threads():
  logs = session.query(ScrapeLog).filter(ScrapeLog.scrape_type == 'thread').order_by("id desc").all()
  return render_template('home.html', logs=logs)

@app.route("/comments")
def comments():
  logs = session.query(ScrapeLog).filter(ScrapeLog.scrape_type == 'comment').order_by("id desc").all()
  return render_template('home.html', logs=logs)

if __name__ == "__main__":
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
