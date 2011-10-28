import xmlrpclib
from optparse import OptionParser
import sys

def main():
    parser = OptionParser(usage="Usage: %prog [options]",
                          version="%prog 1.0")
    parser.add_option("-i", "--id",
                      action="store",
                      dest="id",
                      default=False,
                      help="Ticket ID to remove")
    parser.add_option("-u", "--user",
                      action="store",
                      dest="user",
                      default=False,
                      help="User for connecting to the XMLRPC service",)
    parser.add_option("-p", "--pass",
                      action="store",
                      dest="passwd",
                      default=False,
                      help="Password for connecting to the XMLRPC service",)
    (options, args) = parser.parse_args()

    remove(options.id, options.user, options.passwd)

def remove( tid, user, passwd ):
    p = xmlrpclib.ServerProxy("https://%s:%s@sourceforge.net/apps/trac/w3af/login/xmlrpc" % (user, passwd))

    p.ticket.delete( tid )
    print 'Removed ticket #%s' % (tid)

if __name__ == '__main__':
    main()
