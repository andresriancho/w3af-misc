import xmlrpclib
import sys
import time
import math

from optparse import OptionParser


def main():
    parser = OptionParser(usage="Usage: %prog [options]",
                          version="%prog 1.0")
    parser.add_option("-i", "--ids",
                      action="store",
                      dest="ids",
                      default=False,
                      help="File with comma separated list of ticket IDs to remove.")
    parser.add_option("-m", "--message",
                      action="store",
                      dest="message",
                      default=False,
                      help="Message to use as comment when marking the bug as fixed.",)
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

    for tid in file( options.ids ).read().split(','):
        tid = tid.strip()
        tid = int(tid)
        fix( tid, options.message, options.user, options.passwd)



# Retry decorator with exponential backoff
def retry(tries, delay=3, backoff=2):
    """Retries a function or method until it returns True.
  
    delay sets the initial delay, and backoff sets how much the delay should
    lengthen after each failure. backoff must be greater than 1, or else it
    isn't really a backoff. tries must be at least 0, and delay greater than
    0."""

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    tries = math.floor(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay # make mutable

            rv = f(*args, **kwargs) # first attempt
            while mtries > 0:
                if rv == True: # Done on success
                    return True

                mtries -= 1      # consume an attempt
                time.sleep(mdelay) # wait...
                mdelay *= backoff  # make future wait longer

                rv = f(*args, **kwargs) # Try again

            return False # Ran out of tries :-(

        return f_retry # true decorator -> decorated function
    return deco_retry  # @retry(arg[, ...]) -> true decorator

@retry(3)
def fix( tid, message, user, passwd ):
    p = xmlrpclib.ServerProxy("https://%s:%s@sourceforge.net/apps/trac/w3af/login/xmlrpc" % (user, passwd))

    mark_as = 'duplicate'

    try:
        ticket_info = p.ticket.get( tid )
        if 'resolution' in ticket_info[3]:
            if ticket_info[3]['resolution'] != 'fixed':
                p.ticket.update(tid, message, {'resolution': mark_as, 'status': 'closed'}, False)
                print 'Changed ticket %s status to %s.' % (tid, mark_as)
            else:
                print 'Ignoring ticket %s (already %s)' % (tid, mark_as)
        else:
            p.ticket.update(tid, message, {'resolution': mark_as, 'status': 'closed'}, False)
            print 'Marked ticket %s as %s.' % (tid, mark_as)

    except:
        return False
    else:
        return True

if __name__ == '__main__':
    main()
