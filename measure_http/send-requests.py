import sys

try:
    from core.data.url.xUrllib import xUrllib
except:
    print 'This script needs to be located inside the w3af trunk directory to work'
    sys.exit(1)

from core.data.parsers.urlParser import url_object
import core.data.kb.config as cf

cf.cf.save('sessionName', 'speed')

uri_opener = xUrllib()

for i in xrange(5000):
    url = url_object( 'http://localhost/' + str(i) )
    uri_opener.GET( url, useCache=False)



