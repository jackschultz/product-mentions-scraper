from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
from run import run_gather_threads, run_gather_comments

sched = BlockingScheduler()

q = Queue(connection=conn)

def gather_threads():
  q.enqueue(run_gather_threads)

def gather_comments():
  q.enqueue(run_gather_comments)

sched.add_job(gather_threads) #run immediately
sched.add_job(gather_threads, 'interval', minutes=30)
#sched.add_job(gather_comments, 'interval', minutes=1)
sched.start()
