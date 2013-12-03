import urllib2

token = '?circle-token=e7815c5184c0ebdec15f0c855c0eb47686b2a093'

for index, url in enumerate(file('urls.txt').readlines()):
    url = url.strip()
    if url:
        xml = urllib2.urlopen(url + token).read()
        file('%s.xml' % index, 'wb').write(xml)


