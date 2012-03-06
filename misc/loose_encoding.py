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
            'W3732': ('Use of errors="ignore" in encode/decode functions',
                      ('When using unicode(), "".encode() and "".decode() it is NOT recommended'
                       ' to use errors="ignore". URL encode the character instead.') )
            }
    options = ()
    # this is important so that your checker is executed before others
    priority = -1 

    def visit_callfunc(self, node):
        """
        Called when a CallFunc node is encountered. 

        See compiler.ast documentation for a description of available nodes:
        http://www.python.org/doc/current/lib/module-compiler.ast.html

        I want to catch calls like this:
            unicode('a')
            unicode('a', errors='ignore')
            'a'.decode()
            'a'.decode(errors='ignore')
            'a'.encode()
            'a'.encode(errors='ignore')

        And I do NOT want to catch calls like this:
            'a'.decode('utf8')
            'a'.encode('utf8')
            unicode('a', 'utf8')
        """
        if isinstance(node.func, astng.Name):
            name = node.func.name
            if name == 'unicode':    
                if len(node.args) == 1:
                    self.add_message('E3731', line=node.lineno)
                if len(node.args) == 1:
                    self.add_message('E3731', line=node.lineno)

def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(LooseEncodingChecker(linter))
        
