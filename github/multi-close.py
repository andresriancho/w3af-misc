"""
Requirements
============

cd /tmp/
git clone https://github.com/stephencelis/ghi.git
cd ghi
gem build ghi.gemspec
sudo gem install ghi-0.9.3.gem
ghi config --auth andresriancho
"""

import subprocess


def close_issue(issue):
    print('Closing #%s' % issue)
    cmd = 'ghi close %s' % issue
    cmd = cmd.split(' ')
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate()


while True:
    try:
        issue = raw_input('Issue to close (ctrl+c to exit): ')
    except KeyboardInterrupt:
        break
    else:
        if issue.isdigit():
            close_issue(issue)
        elif '-' in issue:
            start = issue.split('-')[0]
            end = issue.split('-')[1]
            for i in xrange(int(start), int(end) + 1):
                close_issue(str(i))
                