import urllib2
import json
import difflib
import pprint

#################
#   Configuration

BANNED_USERS = []
BANNED_MESSAGES = []

#################

class twitter_message(object):
    def __init__( self, username, text, message_id ):
        self.username = username
        self.text = text
        self.message_id = message_id

    def is_valid( self ):
        #   Parse the message text
        if not self.text.startswith('#w3af_contest'):
            return False
        
        if len(self.text.split(' ')) < 3:
            return False

        return True

    def get_error_message( self ):
        return ' '.join(self.text.split(' ')[2:])

    def __eq__( self, other ):
        s = difflib.SequenceMatcher(None, self.get_error_message(), other.get_error_message())
        r = s.ratio()
        if r > 0.4:
            return True

        return False
        

url = 'http://search.twitter.com/search.json?q=%23w3af_contest'

response = urllib2.urlopen( url )
json_str = response.read()

parsed_json = json.read( json_str )

twitter_message_list = []

for result in parsed_json['results']:
    username = result['from_user']
    text = result['text']
    message_id = result['id']
    tm = twitter_message( username, text, message_id)
    if tm.is_valid():
        #print 'Appending message with text: "' + tm.text + '".'
        twitter_message_list.append(tm)
    else:
        print 'The message sent by "'+tm.username+'" with text: "' + tm.text + '" is invalid.'


#
#   Now that I have all the messages in Python objects, I'll handle them.
#
filtered_message_list = []

#   The messages are in the incorrect order for what I want to do (inverse timeline: newest first)
twitter_message_list.reverse()

for m in twitter_message_list:

    if m.username in BANNED_USERS:
        print 'Ignoring message from "' + m.username + '".'
        continue

    if m.message_id in BANNED_MESSAGES:
        print 'Ignoring message id "' + str(m.message_id) + '".'
        continue

    if not m in filtered_message_list:
        filtered_message_list.append( m )
    else:
        #   We seem to have a dup. Lets ask the user what to do next.
        for m2 in filtered_message_list:
            if m2 == m:
                break
        msg = 'It seems that "'+ m.username +'" sent a duplicated error. Message text: "' + m.get_error_message() + '".'
        msg += ' Which is really similar to: "' + m2.get_error_message() + '" that was previously sent by "' + m2.username
        msg += '". Do you want to allow this error string? [yes|NO]'
        yes_no = raw_input( msg )
        if yes_no == 'yes':
            print 'Allowing "dup".'
            filtered_message_list.append( m )
        else:
            should_be_filtered = True
            print 'Ignoring dup.'

#
#   Now count who is winning
#
errors_sent = {}
errors = {}

for m in filtered_message_list:
    if m.username not in errors_sent:
        errors_sent[ m.username ] = 1
        errors[ m.username ] = [ m.text, ]
    else:
        errors_sent[ m.username ] += 1
        errors[ m.username ].append( m.text )


pp = pprint.PrettyPrinter(indent=4)
print
print 'The winners are:'
print '================'
pp.pprint( errors_sent )
print

print 'The errors are:'
print '==============='
pp.pprint( errors )

