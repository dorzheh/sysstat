#!/usr/bin/env python
#
###############
# Files stats
###############

"""FILE STATISTICS:
   fhalloc    -  Number of allocated file handles.
   fhfree     -  Number of free file handles.
   fhmax      -  Number of maximum file handles.
   inalloc    -  Number of allocated inodes.
   infree     -  Number of free inodes.
   inmax      -  Number of maximum inodes.
   dentries   -  Dirty directory cache entries.
   unused     -  Free diretory cache size.
   agelimit   -  Time in seconds the dirty cache 
                 entries can be reclaimed.
   wantpages  -  Pages that are requested by the system
                 when memory is short.
	
   USAGE:
   newObj = FileStats()      ## Creates an object
   newObj.get_file_stats()   ## Gather statistics
"""

import sys
import re

class FileStats:
     """FileStats class.   
	Exported methodes:
	get_file_stats()   
     """   

     def __init__(self):
         """Constructor"""
         self.files = {'file_nr' : '/proc/sys/fs/file-nr',
                       'inode_nr': '/proc/sys/fs/inode-nr',
                       'dentries': '/proc/sys/fs/dentry-state'}
					   
	 self.list1  = ('fhalloc', 'fhfree', 'fhmax')
	 self.list2  = ('inalloc', 'infree')
	 self.list3  = ('dentries', 'unused', 'agelimit', 'wantpages')

     def get_file_stats(self,line=[],stats={}):
         """The main function.Gather the statistics""" 
         file = self.files
         p = re.compile(r"\s+")
         try:
             f = open(file['file_nr'],'r')
         except IOError:
	     print "Unable to open file %s" % (file['file_nr'])
	     sys.exit(1)
        
         line = map(int,p.split(f.read().strip()))
         stats['file_nr'] = dict(zip(self.list1,line))
         f.close()
 
         try:
             f = open(file['inode_nr'],'r')
         except IOError:
             print "Unable to open the file %s" % (file['inode_nr'])
             sys.exit(1)

         line = map(int,p.split(f.read().strip()))        
         stats['inode_nr'] = dict(zip(self.list2,line))
         stats['inode_nr']['inmax'] = int(stats['inode_nr']['inalloc'])\
                                    + int(stats['inode_nr']['infree'])
         f.close()
        
         try:
	     f = open(file['dentries'],'r')
         except IOError:
	     print "Unable to open the file %s" % (file['dentries'])
             sys.exit(1)
         
         line = map(int,p.split(f.read().strip()))
         stats['dentries'] = dict(zip(self.list3,line))
         f.close()
 
         return stats

		
if __name__ == "__main__":
   o = FileStats() 
   print o.get_file_stats()
