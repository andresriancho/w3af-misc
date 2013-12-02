#!/usr/bin/env python

'''
Tag tests so they don't run in CircleCI, basically means adding two lines
to a test case:

    * The import: "from nose.plugins.attrib import attr"
    * The tag: "@attr('ci_fails')"
    
Input for this script is taken from an input file which holds the filename
and test method to be tagged:

    foo.py:test_abc

And then the file foo.py originally looks like:

    import unittest
    
    class TestFoo(unittest.TestCase):
        def test_abc(self):
            pass
            
After running this script the file will look like:

    from nose.plugins.attrib import attr
    import unittest
    
    class TestFoo(unittest.TestCase):
        @attr('ci_fails')
        def test_abc(self):
            pass

The script is idempotent.
'''
import os
import argparse


TAG = "@attr('ci_fails')"
IMPORT = "from nose.plugins.attrib import attr"
FROM_IMPORT = 'from '
IMPORT_IMPORT = 'import '

HEADER = """02110-1301  USA"""

def tag_file(fname, method_name):
    add_import(fname)
    add_tag_to_method(fname, method_name)

def add_import(fname):
    fcontent = file(fname).read()
    result = []
    
    if IMPORT not in fcontent:
        
        if FROM_IMPORT in fcontent:
            for line in fcontent.splitlines():
                if line.startswith(FROM_IMPORT):
                    result.append(IMPORT)
                    result.append(line)
                else:
                    result.append(line)
        
        elif IMPORT_IMPORT in fcontent:
            for line in fcontent.splitlines():
                if line.startswith(IMPORT_IMPORT):
                    # Different order than before
                    result.append(line)
                    result.append(IMPORT)
                else:
                    result.append(line)
            
    file(fname, 'w').write('\n'.join(result))

def add_tag_to_method(fname, method):
    fcontent = file(fname).read()
    result = []
    previous_was_tag = False
    
    method_match = '    def %s(' % method
    
    for line in fcontent.splitlines():
        if method_match in line and not previous_was_tag:
            tag_line = get_number_of_spaces(line, method) * ' ' + TAG
            result.append(tag_line)
            result.append(line)
        else:
            result.append(line)
        
        previous_was_tag = TAG in line
            
    file(fname, 'w').write('\n'.join(result))

def get_number_of_spaces(method_line, method_name):
    method_signature = 'def %s(' % method_name
    return method_line.find(method_signature)

def get_tag_targets(input_file):
    '''
    Read the file passed as argument and return a list with filenames and
    tags to apply.
    '''
    result = []
    for line in file(input_file):
        fname, method = line.split(',')
        result.append((fname, method))
        
    return result

def parse_args():
    parser = argparse.ArgumentParser(description='Massive tagging of test cases.')
    
    parser.add_argument('--input', help='Filename which contains filename,method',
                        required=True, dest='input_file')

    namespace = parser.parse_args()
    
    return namespace.input_file

if __name__ == '__main__':
    input_file = parse_args()
    tag_targets = get_tag_targets(input_file)
    
    for fname, method_name in tag_targets:
        tag_file(fname, method_name)
        