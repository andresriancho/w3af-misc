'''
gevent_url.py

Copyright 2012 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
from threading import Thread

import urllib2
import gevent
import gevent.queue
from gevent import monkey
from gevent.queue import JoinableQueue

# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all(dns=False)

NUM_WORKER_THREADS = 50

import Queue
import sys
import threading
import time


class WorkerPool(object):

    Exit = NotImplemented
    Queue = NotImplemented

    def start_thread(self):
        raise NotImplementedError

    def __init__(self, maxsize):
        self.queue = self.Queue(maxsize)
        self.threads = [self.start_thread() for i in xrange(maxsize)]

    def _process(self):
        """The main loop of a worker thread."""
        while True:
            func, args, kwargs = self.queue.get()
            try:
                func(*args, **kwargs)
            except self.Exit:
                break
            except Exception, exc:
                import traceback
                traceback.print_exc()
            finally:
                self.queue.task_done()

    def spawn(self, func, *args, **kwargs):
        self.queue.put((func, args, kwargs))

    def join(self):
        self.queue.join()

    def die(self):
        raise self.Exit

    def kill(self, block=True):
        for t in self.threads:
            self.spawn(self.die)
        if block:
            self.join()


class ThreadPool(WorkerPool):

    Exit = SystemExit
    Queue = Queue.Queue

    def start_thread(self):
        t = threading.Thread(target=self._process)
        t.daemon = True
        t.start()
        return t


class GreenletPool(WorkerPool):

    Exit = gevent.GreenletExit
    Queue = gevent.queue.JoinableQueue

    def start_thread(self):
        gl = gevent.spawn(self._process)
        gevent.sleep(0)
        return gl


def report(model, concurrency, number, total_time):
    print "%s\t%d\t%d\t%.8f" % (model, concurrency, number, total_time)


def print_head(url):
    #print ('Starting %s' % url)
    try:
        data = urllib2.urlopen(url).read()
    except urllib2.HTTPError:
        pass

def main():

    concurrency = 100
    number = 5000
    
    for model in ('gevent', 'threads'):
        
        if model == 'gevent':
            pool = GreenletPool(concurrency)
        else:
            pool = ThreadPool(concurrency)
    
        start_time = time.time()
        for i in xrange(number):
            pool.spawn(print_head, 'http://127.0.0.1/' + str(i))
        pool.join()
        end_time = time.time()
        total_time = end_time - start_time
        print >>sys.stderr, "Total time: %.5f seconds" % (total_time,)
        pool.kill()
        report(model, concurrency, number, total_time)


if __name__ == '__main__':
    main()