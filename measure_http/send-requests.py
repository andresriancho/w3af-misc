import time
import sys

from measure import show_stats

NUM_REQUESTS = 5000

try:
    from core.data.url.xUrllib import xUrllib
except:
    print 'This script needs to be located inside the w3af trunk directory to work'
    sys.exit(1)

from core.data.parsers.urlParser import url_object
import core.data.kb.config as cf

cf.cf.save('sessionName', 'speed')

uri_opener = xUrllib()

start_time = time.time()

for i in xrange(NUM_REQUESTS):
    url = url_object( 'http://localhost/' + str(i) )
    uri_opener.GET( url, useCache=False)

end_time = time.time()

show_stats( start_time, end_time, NUM_REQUESTS)



