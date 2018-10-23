from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
from run import run_gather_reddit_threads, run_gather_reddit_comments, run_gather_hacker_news_comments

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

sched = BlockingScheduler()

q = Queue(connection=conn)

#Reddit
def gather_reddit_threads():
  q.enqueue(run_gather_reddit_threads)

def gather_reddit_comments():
  q.enqueue(run_gather_reddit_comments)

sched.add_job(gather_reddit_comments)
sched.add_job(gather_reddit_comments, 'interval', seconds=50)
sched.add_job(gather_reddit_threads)
sched.add_job(gather_reddit_threads, 'interval', minutes=15)

#HackerNews
def gather_hacker_news_comments():
  q.enqueue(run_gather_hacker_news_comments)

sched.add_job(gather_hacker_news_comments)
sched.add_job(gather_hacker_news_comments, 'interval', minutes=5)


sched.start()

