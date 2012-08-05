from urlparse import urlparse
from threading import Thread
import httplib, sys
import urllib2
from Queue import Queue

import time
from measure import show_stats

NUM_REQUESTS = 5000

concurrent = 200

def doWork():
    while True:
        url=q.get()
        data=GET(url)
        doSomethingWithResult(data)
        q.task_done()

def GET(url):
    try:
        data = urllib2.urlopen(url).read()
    except urllib2.HTTPError:
        pass
    else:
        return data

def doSomethingWithResult(data):
    pass

q=Queue(concurrent*2)
for i in range(concurrent):
    t=Thread(target=doWork)
    t.daemon=True
    t.start()

start_time = time.time()

for i in xrange(NUM_REQUESTS):
    q.put('http://127.0.0.1/' + str(i))

q.join()

end_time = time.time()

show_stats( start_time, end_time, NUM_REQUESTS)

