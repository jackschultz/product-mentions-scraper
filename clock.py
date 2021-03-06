from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
from run import run_gather_threads, run_gather_comments

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

sched = BlockingScheduler()

q = Queue(connection=conn)

def gather_threads():
  q.enqueue(run_gather_threads)

def gather_comments():
  q.enqueue(run_gather_comments)

sched.add_job(gather_comments)
sched.add_job(gather_comments, 'interval', seconds=50)
sched.add_job(gather_threads)
sched.add_job(gather_threads, 'interval', minutes=15)
sched.start()

