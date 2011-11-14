from datetime import datetime
from operator import methodcaller
import copy
import difflib
import re
import xmlrpclib

SF_TRAC_URL = \
    "https://%(user)s:%(passwd)s@sourceforge.net/apps/trac/w3af/login/xmlrpc"
credentials = {
    'user': "w3afbugsreport",
    'passwd': "w3afs1nce2006"
    }
server = None
tickets = []

def get_trac_ticket_ids(topid=None):
    if topid is None:
        topid = 175000
    step = 100
    tickets = []
    for tid in xrange(120000, topid, step):
        args = '|'.join(str(i) for i in xrange(tid, tid+step))
        tickets += server.ticket.query(
                        'status=new&component=automatic-bug-report&id=' + args
                        )
        
    return tickets
    
def get_tickets_data(*tids):
    resp = []
    multicalldict = {'methodName': 'ticket.get', 'params': None}
    multiparams = []
    
    for i in xrange(0, len(tids), 100):
        for tid in tids[i:i+100]:
            d = copy.copy(multicalldict)
            d['params'] = [tid]
            multiparams.append(d)
        
        # Exec query
        for tkt in server.system.multicall(multiparams):
            tkt = tkt[0]
            dd = {'create_date': tkt[1],
                  'summary': tkt[3]['summary'],
                  'reporter': tkt[3]['reporter'],
                  'status': tkt[3]['status'],
                  'id': tkt[0]}
            resp.append(dd)
        
        # Clean it!
        multiparams = []
    return resp

def group_tickets(tickets, simrules=()):
    groups = []
    removed = set()
    
    for pos, tkt in enumerate(tickets):
        if tkt['id'] in removed:
            continue

        subgroup = [tkt]
        removed.add(tkt['id'])
        
        for tkt2 in tickets[pos+1:]:
            if tkt2['id'] in removed:
                continue
            for rule in simrules:
                if rule(tkt, tkt2):
                    subgroup.append(tkt2)
                    removed.add(tkt2['id'])
                    break
        groups.append(subgroup)
    return groups

def log_tickets(grouped_tickets):
    # Typically a list of lists
    for subgrp in grouped_tickets:
        tkt = subgrp[0]
        print '%s [%s] <-> %s' % (tkt['id'], len(subgrp), tkt['summary'])
        print
#        for tkt in subgrp:
#            print '%s [%s] <-> %s' % (tkt['id'], tkt['summary'])
#        print '*'*80

def load_ticket_ids():
    try:
        from created_tickets import tickets
    except ImportError:
        tickets = []
    return tickets

def server_login():
    global server
    server = xmlrpclib.ServerProxy(SF_TRAC_URL % credentials)

if __name__ == '__main__':
    ## Group-by similarity rules ##
    def sim_on_summ_without_user_input(summ, other_summ):
        patt = '\[Auto\-Generated\] Bug Report \- \w{32}'
        return bool(re.match(patt, summ['summary']) and
                    re.match(patt, other_summ['summary']))
    
    sim_on_difflib = (lambda x, y: difflib.SequenceMatcher(
                        None, x['summary'], y['summary']).quick_ratio() > .90)
    rules = (sim_on_summ_without_user_input, sim_on_difflib)
    
    # First, do login
    server_login()
    
    # Get tickets
    ticket_ids = load_ticket_ids()#[5000: 5100]
    if not ticket_ids:
        ticket_ids = get_trac_ticket_ids()
        # TODO: Save it to Disk
    last_date = datetime(2011, 1, 1)
    tickets = filter(
            lambda t: datetime(*t['create_date'].timetuple()[:6]) > last_date,
            get_tickets_data(*ticket_ids)
            )
    # Print report
    log_tickets(
        reversed(sorted(
                group_tickets(tickets, simrules=rules),
                key=methodcaller('__len__')
                )
            )
        )