import os
import xunitparser
import subprocess
import shlex


def get_full_path_for_file(fname):
    '''
    Find the directory where a file lives and return the full directory + fname
    '''
    cmd = 'find . -name %s' % fname
    try:
        output = subprocess.check_output(shlex.split(cmd), cwd='../')
    except Exception, e:
        print 'Error %s' % e
        return None
    else:
        if len(output.splitlines()) > 1:
            return None

        print output
        return output.strip()

output = file('disable.txt', 'w')

for fname in os.listdir('.'):
    if fname.endswith('.xml'):
        try:
            ts, tr = xunitparser.parse(open(fname))
            for test in ts._tests:
                if not test.success:
                    test_file = '/'.join(test.classname.split('.')[:-1]) + '.py'
                    test_method = test.methodname

                    if '/' not in test_file:
                        full_file = get_full_path_for_file(test_file)
                        if full_file:
                            test_file = full_file

                    output.write('%s,%s\n' % (test_file, test_method))
        except Exception, e:
            print 'Failed %s %s' % (fname, e)
        else:
            print 'Processed %s' % fname

