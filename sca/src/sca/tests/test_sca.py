'''
Created on Feb 28, 2011

@author: jandalia
'''

from pymock import PyMockTestCase, method, override, dontcare, set_count

from ..sca import PhpSCA, VariableDef

class TestPHPSCA(PyMockTestCase):
    '''
    Test unit for php static code analyzer
    '''
    
    def setUp(self):
        PyMockTestCase.setUp(self)

    def test_vars(self):
        code = '''
            <?
              $foo = $_GET['bar'];
              $spam = $_POST['blah'];
              $eggs = 'blah' . 'blah';
              if ($eggs){
                  $xx = 'waka-waka';
                  $yy = $foo;
              }
            ?>
            '''
        analyser = PhpSCA(code, debugmode=True)
        analyser.start()
        # Get all vars
        vars = analyser.get_vars(usr_controlled=False)
        self.assertEquals(5, len(vars))
        # Get user controlled vars
        usr_cont_vars = analyser.get_vars(usr_controlled=True)
        self.assertEquals(3, len(usr_cont_vars))
        # Test $foo
        foovar = usr_cont_vars[0]
        self.assertEquals('$foo', foovar.name)
        self.assertTrue(foovar.controlled_by_user)
        self.assertFalse(foovar.is_root)
        self.assertTrue(foovar.parent)
        # Test $spam
        spamvar = usr_cont_vars[1]
        self.assertEquals('$spam', spamvar.name)
        # Test $spam
        yyvar = usr_cont_vars[2]
        self.assertEquals('$yy', yyvar.name)
    
    def test_override_var(self):
        code = '''
        <?php
            $var1 = $_GET['param'];
            $var1 = 'blah';
            
            $var2 = escapeshellarg($_GET['param2']);
            
            $var3 = 'blah';
            if ($x){
                $var3 = $_POST['param2'];
            }
            else{
                $var3 = 'blah'.'blah'; 
            }
        ?>
        '''
        analyser = PhpSCA(code, debugmode=True)
        analyser.start()
        vars = analyser.get_vars(usr_controlled=False)
        var1 = vars[0]
        self.assertFalse(var1.controlled_by_user)
        # 'var2' is controlled by the user but is safe for OS-Commanding
        var2 = vars[1]
        self.assertTrue(var2.controlled_by_user)
        self.assertTrue('OS_COMMANDING' in var2._safe_for)
        # 'var3' must still be controllable by user
        var3 = vars[2]
        self.assertTrue(var3.controlled_by_user)
    
    def test_vuln_functions(self):
        pass
    
    def test_syntax_error(self):
        pass
    
    

