from datetime import datetime
from operator import methodcaller
import cgi
import copy
import difflib
import re
import xmlrpclib

HTML_OUTPUT_TEMP = '''<html>
<head>
<title>Tickets Summary</title>
</head>
<body>
<ul>
%(tickets)s
</ul>
<body>
</html>
'''
TICKETS_LI = '''
<li>
    <span title="%(desc)s"><b>[%(rank)s] %(short_desc)s</b><br>
    &nbsp;&nbsp;&nbsp;&nbsp;<span style="font-size: 10pt">%(tickets)s
    </span><br>&nbsp;
</li>'''

TICKET_ALINK = \
  '<a href="https://sourceforge.net/apps/trac/w3af/ticket/%(id)s">%(id)s</a>'

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

def save_ticket_ids(tids):
    with open('created_tickets.py', 'wb') as f:
        f.write('tickets = ' + str(tids))
    
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
    
    tickets = []
    # Typically a list of lists
    for subgrp in grouped_tickets:
        desc = cgi.escape(subgrp[0]['summary'][30:].encode('utf-8'), True)
        tickets.append(
           TICKETS_LI % {
                'rank': len(subgrp),
                'desc': desc,
                'short_desc': (desc[:100] + '...') \
                                    if len(desc) > 100 else desc,
                'tickets': ',\n'.join([TICKET_ALINK % tkt for tkt in subgrp])
                }
            )
    
    output = HTML_OUTPUT_TEMP % {'tickets': ''.join(tickets)}
    
    with open('bugs_ranking.html', 'wb') as f:
        f.write(output)

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
                        None, x['summary'], y['summary']).quick_ratio() > .95)
    rules = (sim_on_summ_without_user_input, sim_on_difflib)
    
    # First, do login
    server_login()
    
    # Get tickets
    ticket_ids = load_ticket_ids()##[3600:3650]
    if not ticket_ids:
        ticket_ids = get_trac_ticket_ids()
        save_ticket_ids(ticket_ids)
    
    start_date = datetime(2011, 1, 1)
    tickets = filter(
            lambda t: datetime(*t['create_date'].timetuple()[:6]) > start_date,
            get_tickets_data(*ticket_ids)
            )
    # Generate report
    log_tickets(
        reversed(sorted(
                group_tickets(tickets, simrules=rules),
                key=methodcaller('__len__')
                )
            )
        )
    print '### DONE!! ###'
