import os

from models import ScrapeLog, Mention, Comment
from session import session

from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/")
def home():
  hour_ago = datetime.now() - timedelta(hours = 1)
  day_ago = datetime.now() - timedelta(hours=24)
  week_ago = datetime.now() - timedelta(days=7)
  logs = session.query(ScrapeLog).order_by("id desc").limit(500)
  hour_mention_count = session.query(Mention).filter(Mention.created_at > hour_ago).count()
  day_mention_count = session.query(Mention).filter(Mention.created_at > day_ago).count()
  week_mention_count = session.query(Mention).filter(Mention.created_at > week_ago).count()
  return render_template('home.html', logs=logs, hour_mention_count=hour_mention_count, day_mention_count=day_mention_count, week_mention_count=week_mention_count)

@app.route("/threads")
def threads():
  logs = session.query(ScrapeLog).filter(ScrapeLog.scrape_type == 'thread').order_by("id desc").limit(500)
  return render_template('home.html', logs=logs)

@app.route("/comments")
def comments():
  logs = session.query(ScrapeLog).filter(ScrapeLog.scrape_type == 'comment').order_by("id desc").limit(500)
  return render_template('home.html', logs=logs)

if __name__ == "__main__":
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
