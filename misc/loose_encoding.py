from logilab import astng

from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker

class LooseEncodingChecker(BaseChecker):
    """
    Verify that the code is properly encoding and decoding strings.
    """
    
    __implements__ = IASTNGChecker

    name = 'custom'
    msgs = {'E3731': ('Use of encoding/decoding WITHOUT specific character encoding.',
                      ('When using unicode() , "".encode() and "".decode() it is required'
                       ' to use a specific encoding instead of the default.')),
            }
    options = ()
    # this is important so that your checker is executed before others
    priority = -1 

    def visit_callfunc(self, node):
        """
        Called when a CallFunc node is encountered. 

        See compiler.ast documentation for a description of available nodes:
        http://www.python.org/doc/current/lib/module-compiler.ast.html
        """
        print dir(node)
        print node.args
        self.add_message('W9901', line=1)

def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(LooseEncodingChecker(linter))
    print 'reg!'
        
