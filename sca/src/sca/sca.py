'''
Created on Feb 28, 2011

@author: jandalia
'''

from phply import phplex
from phply.phpparse import parser 
import phply.phpast as phpast


# We prefer our way. Slight modification to original method.
# Now we can now know which is the parent of the current node
# while the AST traversal takes place.
Node = phpast.Node

def accept(nodeinst, visitor):
    visitor(nodeinst)
    for field in nodeinst.fields:
        value = getattr(nodeinst, field)
        if isinstance(value, Node):
            # Add parent
            value._parent_node = nodeinst
            value.accept(visitor)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, Node):
                    # Add parent
                    item._parent_node = nodeinst
                    item.accept(visitor)
Node.accept = accept


class PhpSCA(object):
    '''
    TODO: Docstring here
    '''

    def __init__(self, code, debugmode=False):
        lexer = phplex.lexer.clone()
        self._ast_code = parser.parse(code, lexer=lexer)
        
        # Define scope
        scope = Scope(parent_scope=None)
        self._user_vars = [VariableDef(uv, -1, scope) for uv in 
                                                        VariableDef.USER_VARS]
        map(scope.add_var, self._user_vars)
        self._scopes = [scope]
        # Function calls
        self._functions = []
    
    def start(self):
        for node in self._ast_code:
            node.accept(self._visitor)
    
    def get_vars(self, usr_controlled=False):
        all_vars = []
        filter_tainted = (lambda v: v.controlled_by_user) if usr_controlled \
                            else (lambda v: 1)
        
        for scope in self._scopes:
            all_vars += filter(filter_tainted, scope.get_all_vars())
            all_vars = list(set(all_vars) - set(self._user_vars))
        
        return all_vars
    
    def get_funcs(self, vuln=False):
        filter_vuln = (lambda f: f.vuln_type != FuncCall.IS_CLEAN) \
                        if vuln else (lambda f: True)
        return filter(filter_vuln, self._functions)
    
    def _visitor(self, node):
        
        currscope = self._scopes[-1]
        
        if type(node) == phpast.FunctionCall:
            fc = FuncCall(node.name, node.lineno, node, currscope)
            self._functions.append(fc)
        
        # Create the VariableDef
        elif type(node) == phpast.Assignment:
            varnode = node.node
            newvar = VariableDef(varnode.name, varnode.lineno,
                                 currscope, ast_node=node)
            currscope.add_var(newvar)
        
##        elif type(node) in (phpast.Function):
##            new_scope = Scope()


class VariableDef(object):
    
    USER_VARS = ('$_GET', '$_POST', '$_COOKIES')
    
    def __init__(self, name, lineno, scope, ast_node=None):
        
        # Might be either 'Assignment' or 'Variable' type
        self._name = name
        self._lineno = lineno
        self._scope = scope
        self._ast_node = ast_node
        self._parent = None
        self._controlled_by_user = None
        self._safe_for = []
        if name in VariableDef.USER_VARS:
            self._is_root = True
        else:
            self._is_root = None
    
    @property
    def lineno(self):
        return self._lineno
    
    @property
    def name(self):
        return self._name

    @property
    def is_root(self):
        '''
        A variable is root when it has no ancestor or when its ancestor's name
        is in USER_VARS
        '''
        if self._is_root is None:
            if self.parent:
                self._is_root = False
            else:
                self._is_root = True
        return self._is_root
    
    @property
    def parent(self):
        '''
        Get this var's parent
        '''
        if self._is_root:
            return None
        
        if self._parent is None:
            # TODO: Check this!
            parent = self._get_ancestor(self._ast_node.expr)
            if parent:
                self._parent = self._scope.get_var(parent.name)
        return self._parent
    
    @property
    def controlled_by_user(self):
        '''
        Returns bool that indicates if this variable is tainted.
        '''
        
        cbusr = self._controlled_by_user
        
        if cbusr is None:
            if self.is_root:
                if self._name in VariableDef.USER_VARS:
                    cbusr = True
                else:
                    cbusr = False
            else:
                cbusr = self.parent.controlled_by_user
            
            self._controlled_by_user = cbusr

        return cbusr
    
    def __eq__(self, ovar):
        return self._lineno == ovar.lineno and self._name == ovar.name
    
    def __hash__(self):
        return hash(self._name)
    
    def is_tainted_for(self, funcname):
        # TODO: Implement this!
        return True
    
    def deps(self):
        '''
        Generator function. Yields this var's dependency.
        '''
        parent = self.parent
        while not parent.is_root:
            yield parent
            parent = parent.parent
    
    # TODO: Refactor this! See below
    def _get_ancestor(self, node):
        '''
        Return this var's ancestor.
        '''
        if type(node) == phpast.Variable:
            # Find out if this var is contained by a "securing" function
            # If this is the case then include mark this variable as 'safe'
            # for that vulnerability.
            parent = getattr(node, '_parent_node', None)
            while parent:
                if type(parent) == phpast.FunctionCall:
                    for vulnty, fnames in FuncCall.SFDB.iteritems():
                        for fn in fnames:
                            if parent.name == fn:
                                self._safe_for.append(vulnty)
                parent = getattr(parent, '_parent_node', None)
            return node
        
        for f in getattr(node, 'fields', []):
            val = getattr(node, f)
            if isinstance(val, phpast.Node):
                val = [val]
            if type(val) is list:
                for ele in val:
                    res = self._get_ancestor(ele)
                    if res:
                        return res


class Scope(object):
    
    def __init__(self, parent_scope=None):
        self._parent_scope = None
        self._vars = {}
        
    def add_var(self, var):
        if self._parent_scope:
            self._parent_scope.add_var(var)
        else:
            if var is None:
                raise ValueError, "Invalid value for parameter 'var': None"
            self._vars[var.name] = var
    
    def get_var(self, varname):
        var = self._vars.get(varname)
        if not var and self._parent_scope:
            var = self._parent_scope.get_var
        return var
    
    def get_all_vars(self):
        return self._vars.values()
    
    def __repr__(self):
        return "Scope [%s]" % ', '.join(v.name for v in self.get_all_vars())


class FuncCall(object):
    
    # Potentially Vulnerable Functions Database
    PVFDB = {
        'OS_COMMANDING': ('system', 'exec', 'shell_exec'),
        'XSS': ('echo', 'print', 'printf', 'header'),
        'FILE_INCLUDE': ('include', 'include_once', 'require', 'require_once'),
        }
    IS_CLEAN = 'IS_CLEAN'
    
    # Securing Functions Database
    SFDB = {
        'OS_COMMANDING': ('escapeshellarg', 'escapeshellcmd'),
        'XSS': ('htmlentities', 'htmlspecialchars'),
        'SQL': ('addslashes', 'mysql_real_escape_string',
                 'mysqli_escape_string', 'mysqli_real_escape_string')
        }
    
    def __init__(self, name, lineno, func_node, scope):
        self._lineno = lineno
        self._name = name
        self._func_node = func_node
        self._scope = scope
        self._vuln_type = self._find_if_vulnerable()
    
    @property
    def vuln_type(self):
        return self._vuln_type
    
    def _find_if_vulnerable(self):
        
        # TODO: Refactor this! See above duplicate code
        def get_var_nodes(node):
            if type(node) == phpast.Variable:
                varnodes.append(node)
            else:
                for f in node.fields:
                    val = getattr(node, f)
                    if isinstance(f, phpast.Node):
                        val = [val]
                    if type(val) is list:
                        for ele in val:
                            get_var_nodes(ele)
        
        for vuln_type, fname in FuncCall.PVFDB.iteritems():
            if self._name == fname:
                varnodes = []
                get_var_nodes(self._func_node)
                for var in varnodes:
                    var = self._scope.get(var.name)
                    if var.controlled_by_user and \
                        var.is_tainted_for(self._name):
                        return vuln_type.upper()
        
        return FuncCall.IS_CLEAN
    