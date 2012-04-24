import os

import Memory
from Trick import Trick


class RemoteOpen(Trick):
    def usage(self):
        return """
        Hooks the open syscall, downloads the remote file to the local file system,
        performs a second open of the local file and returns that file handler to
        the hooked process.
        """
    
    def callbefore(self, pid, call, args):
        '''
        Entry point for the trick.
        @return: None
        '''
        m = Memory.getMemory(pid)
        arg_mem_addr_path = args[0]
        arg_flags = args[1]
        arg_mode = args[2]
        
        try:
            filename = m.get_string( arg_mem_addr_path )
        except:
            pass
        else:
        
            if not self._is_library( filename ):
            
                local_filename = self._download_file( filename )

                area, area_size = m.areas()[0]
                m.poke(area, local_filename + '\0')
        
                return (None, None, None, (area, arg_flags, arg_mode) )
        
        return None

    def _is_library( self, filename ):
        '''
        @return: True if the filename I'm getting is (usually) a library.
        '''
        if 'passwd' in filename:
          return False
        
        return True
        
    def _download_file( self, original_filename ):
        '''
        Downloads the file to the local file system.
        @return: The local full path.
        '''
        print 'working!', original_filename
        
        import shutil
        
        directory = os.path.dirname(original_filename)
        filename = os.path.split(original_filename)[1]
        target_directory = os.path.join( '/tmp/cache/', directory[1:] )
        target_filename = os.path.join( target_directory, filename )
        
        try:
            os.makedirs( target_directory  )
        except:
            # The directory might be already there!
            pass
        
        try:
            shutil.copyfile( original_filename, target_filename )
        except Exception, e:
            print e
        
        content = file( target_filename ).read()
        o = file( target_filename, 'w')
        o.write ( content[::-1] )
        o.close()
        
        return target_filename

    def callmask(self):
        return { 'open' : 1 }
