import urllib2
import json
import difflib

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

        if len(self.get_error_message()) < 5:
            return False

        return True

    def get_error_message( self ):
        return ' '.join(self.text.split(' ')[:3])

    def __eq__( self, other ):
        s = difflib.SequenceMatcher(None, self.get_error_message(), other.get_error_message())
        r = s.ratio()
        if r > 0.6:
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
        print 'The message with text: "' + tm.text + '" is invalid.'


#
#   Now that I have all the messages in Python objects, I'll handle them.
#
filtered_message_list = []

#   The messages are in the incorrect order for what I want to do (inverse timeline: newest first)
twitter_message_list.reverse()

for m in twitter_message_list:
    if not m in filtered_message_list:
        filtered_message_list.append(m)
    else:
        #   We seem to have a dup. Lets ask the user what to do next.
        for m2 in filtered_message_list:
            if m2 == m:
                break
        msg = 'It seems that "'+ m.username +'" sent a duplicated error. Message text: "' + m.text + '".'
        msg += ' Which is really similar to: "' + m2.text + '" that was previously sent by "' + m2.username
        msg += '". Do you want to allow this error string? [yes|no]'
        yes_no = raw_input( msg )
        if yes_no == 'yes':
            print 'Allowing "dup".'
            filtered_message_list.append(m)
        else:
            print 'Ignoring dup.'

#
#   Now count who is winning
#
errors_sent = {}

for m in filtered_message_list:
    if m.username not in errors_sent:
        errors_sent[ m.username ] = 1
    else:
        errors_sent[ m.username ] += 1

print errors_sent

