#!/usr/bin/env python
#
##########################
# SWAP and paging stats
##########################


"""PAGES AND SWAP STATISTICS:
   pgpgin     -  Number of kilobytes the system
                 has paged in from disk per second.
   pgpgout    -  Number of kilobytes the system has
                 paged out to disk per second.
   pswpin     -  Number of kilobytes the system has
                 swapped in from disk per second.
   pswpout    -  Number of kilobytes the system has
                 swapped out to disk per second.

   The following statistics are only available by kernels from 2.6.

   pgfault    -  Number of page faults the system has
                 made per second (minor + major).
   pgmajfault -  Number of major faults per second the
                 system required loading a memory page from disk.

   USAGE:
   newObj = PgSwStats()      ## Creates an object
   newObj.initialize()       ## Initialize statistics
   newObj.get_pgsw_stats()   ## Gather statistics
"""   


import re
import sys


class PgSwStats: 
    """PgSwStats class.	 
       Exported methods:
       initialize()
       get_pgsw_stats()
    """   
    
    def __init__(self):
        """Constructor"""	
        self.files = { 'stat'   : '/proc/stat',
                       'vmstat' : '/proc/vmstat',
                       'uptime' : '/proc/uptime' }
  

    def initialize(self):
	"""Initialize the statistics"""
        self.uptime = self._uptime()
        self.init   = self._load()

    def get_pgsw_stats(self):
	"""The main function.Gather the statistics"""
	if not self.init:
            print "There are no initial statistics defined"
            sys.exit(1)
        self.stats = self._load()
        self._deltas()
        return self.stats

#
#  Private stuff
#
    def _load(self,stats={}):
        """Load statistics"""
        file = self.files

	try:
            f = open(file['stat'])
	except IOError:
            print "Unable to open the file %s" % (file['stat'])
            sys.exit(1)

        exprpg = re.compile(r"^page\s+(\d+)\s+(\d+)$")
	exprsw = re.compile(r"^swap\s+(\d+)\s+(\d+)$")
	for line in f.readlines():
	    m = exprpg.search(line)
	    if m:
	        ks = ('pgpgin','pgpgout')
	        vs = (m.group(1),m.group(2))
                stats['page'] = dict(zip(ks,vs))   
            m = exprsw.search(line)
            if m:
	         ks = ('pswpin','pswpout')
		 vs = (m.group(1),m.group(2))
                 stats['swap'] = dict(zip(ks,vs)) 
        f.close()

	# If paging and swapping are not found in /proc/stat
        # then let's try the /proc/vmstat file (since the 2.6 kernel)
        if not stats['swap']['pswpout']:
            try:
	        f = open(file['vmstat'],'r') 
    	    except IOError:
	        print "Unable to open the file %s" % (file['vmstat'])
	        sys.exit(1)
	    cmpldexpr = re.compile(r"^(pgpgin|pgpgout|pswpin|pswpout|pgfault|pgmajfault)\s+(\d+)") 
            for line in f.readlines():
                m = cmpldexpr.search(line)
                if not m:
                    continue
                stats['vmstat'][m.group(1)] = m.group(2)
            f.close()

        return stats

    def _deltas(self):  
        """Find a delta between initial and final states"""
        istat       = self.init
        lstat       = self.stats
        uptime      = self._uptime()
        self.uptime = uptime

        delta  = self._sprintf('%.2f', float(uptime) - float(self.uptime))
        delta = 1.1
        for key,value in lstat.items():
            for subkey,subval in value.items():
                if not istat[key][subkey] and not lstat[key][subkey]:
	            print "Different keys in statistics"
	            sys.exit(1)

                if not subval.isdigit() and not\
                    istat[key][subkey].isdigit():			
                    print "Value of 'subkey' is not a number"
        	    sys.exit(1)
                if lstat[key][subkey] == istat[key][subkey]:
                    lstat[key][subkey] = self._sprintf('%.2f',0)
                elif delta > 0:
                    lstat[key][subkey] = self._sprintf \
                    ('%.2f',(float(lstat[key][subkey])\
                    - float(istat[key][subkey])) / float(delta))
                else:
	            lstat[key] = self._sprintf('%.2f',lstat[key][subkey]\
                                 - istat[key][subkey])
                istat[key][subkey] = subval
        return istat

    def _uptime(self):
        """Determine an uptime and idle time""" 
        file = self.files
	try:
            f = open(file['uptime'],'r')
        except IOError:
	    print "Unable to open the file %s" % (file['uptime'])
            sys.exit(1)

        up, idle = f.read().split(' ')
        f.close()

        return up

    def _sprintf(self, format,*args):
        """String formatting"""
        return format % (args)


if __name__ == "__main__":
   newObj = PgSwStats()          ## Creates an object
   newObj.initialize()           ## Initialize statistics
   import time
   time.sleep(2)
   print newObj.get_pgsw_stats() ## Gather statistics

