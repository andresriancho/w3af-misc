from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient
import time

count = 0

def handle_request(response):
    if response.error:
        #print "Error:", response.error
        pass
    else:
        body = response.body

    if count == 4999:
        ioloop.IOLoop.instance().stop()

http_client = AsyncHTTPClient()

for i in xrange(5000):
    count += 1
    url = "http://127.0.0.1/" + str(i)
    http_client.fetch(url, handle_request)

ioloop.IOLoop.instance().start()

