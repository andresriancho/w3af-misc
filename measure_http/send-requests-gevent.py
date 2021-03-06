#!/usr/bin/python

from measure import show_stats
import time

import gevent
from gevent import monkey
from gevent.queue import JoinableQueue

# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all(dns=False)

import urllib2

def print_head(url):
    #print ('Starting %s' % url)
    try:
        data = urllib2.urlopen(url).read()
    except urllib2.HTTPError:
        pass
    #print ('%s: %s bytes: %r' % (url, len(data), data[:50]))

def worker():
    while True:
        url = q.get()
        try:
            print_head(url)
        finally:
            q.task_done()

NUM_WORKER_THREADS = 50
NUM_REQUESTS = 5000

q = JoinableQueue()
for i in range(NUM_WORKER_THREADS):
     gevent.spawn(worker)

start_time = time.time()

for i in xrange(NUM_REQUESTS):
    url = 'http://127.0.0.1/' + str(i)
    q.put(url)

q.join()  # block until all tasks are done

end_time = time.time()

show_stats( start_time, end_time, NUM_REQUESTS)

