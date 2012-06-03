from twisted.internet import reactor, threads
from urlparse import urlparse
import urllib2
import itertools

concurrent = 200
finished=itertools.count(1)
reactor.suggestThreadPoolSize(concurrent)

def GET(url):
    try:
        data = urllib2.urlopen(url).read()
    except urllib2.HTTPError:
        pass
    else:
        return data

def processResponse(response,url):
    #print response, url
    processedOne()

def processError(error,url):
    #print "error", url#, error
    processedOne()

def processedOne():
    if finished.next()==added:
        reactor.stop()

def addTask(url):
    req = threads.deferToThread(GET, url)
    req.addCallback(processResponse, url)
    req.addErrback(processError, url)   

added=0
for i in xrange(5000):
    added+=1
    addTask('http://127.0.0.1/' + str(i))

try:
    reactor.run()
except KeyboardInterrupt:
    reactor.stop()
