import xmlrpclib
from optparse import OptionParser
import sys

def main():
    parser = OptionParser(usage="Usage: %prog [options]",
                          version="%prog 1.0")
    parser.add_option("-u", "--user",
                      action="store",
                      dest="user",
                      default=False,
                      help="Username for connecting to the XMLRPC service")
    parser.add_option("-p", "--pass",
                      action="store",
                      dest="passwd",
                      default=False,
                      help="Password for connecting to the XMLRPC service",)
    (options, args) = parser.parse_args()

    anti_spam(options.user, options.passwd)

def anti_spam( user, passwd ):
    p = xmlrpclib.ServerProxy("https://%s:%s@sourceforge.net/apps/trac/w3af/login/xmlrpc" % (user, passwd))

    #
    #   IMPORTANT: Please note that this script should be run more than once, since the query returns
    #   100 items, and you might have more than that in your Trac instance. I could make it return more
    #   tickets... but the process would be too long and I would get bored.
    #
    r = p.ticket.query("milestone=1.0&status!=closed")
    to_remove = []
    to_show = []

    sys.stdout.write('Loading %s tickets' % len(r) )
    sys.stdout.flush()
    for count, tid in enumerate(r):
        tdata = p.ticket.get(tid)
        desc = tdata[3]['description']
        to_show.append( (tid,desc) )
        sys.stdout.write('.')
        if count % 10 == 0:
            sys.stdout.write('%s' % count)
        sys.stdout.flush()

    print 'Choose tickets to remove:'

    for count, (tid, desc) in enumerate(to_show):
        print '%s description: """%s"""' % ( tid, desc )

        remove = raw_input("Remove ticket #%s (%s/%s)? (y/Y)" % (tid, count+1, len(to_show)) )
        if remove.lower() == 'y' or remove == '':
            to_remove.append( tid )

    for count, tid in enumerate(to_remove):
        p.ticket.delete( tid )
        print 'Removed ticket #%s (%s/%s)' % (tid, count+1, len(to_remove))

if __name__ == '__main__':
    main()
