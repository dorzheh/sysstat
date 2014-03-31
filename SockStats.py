#!/usr/bin/env python
#
###############
# Socket stats
###############

"""SOCKETS STATISTICS:
   used    -  Total number of used sockets.
   tcp     -  Number of tcp sockets in use.
   udp     -  Number of udp sockets in use.
   raw     -  Number of raw sockets in use.
   ipfrag  -  Number of ip fragments in use.
	
   USAGE:
   newObj = SockStats()      ## Creates an object
   newObj.get_sock_stats()   ## Gather statistics	
"""	

import re
import sys

class SockStats:
    """SockStats class.
       Exported methodes:
       get_sock_stats()
    """
	
    def __init__(self):
	"""Constructor""" 
        self.files = {'sockstats' : '/proc/net/sockstat'}

    def get_sock_stats(self, stats={}):
	"""The main function.Gathers resuired statistics"""
        file = self.files
        stats['sockstats'] = {}
		
        try:
            f = open(file['sockstats'],'r')
        except IOError:
            print "Unable to open the file %s" % (file['sockstats'])
	    sys.exit(1)

        for line in f:
            m = re.search(r"sockets: used (\d+)",line)
            if m:
                 stats['sockstats']['used'] = int(m.group(1))
            else:
                 m = re.search(r"TCP: inuse (\d+)",line)
                 if m:
                      stats['sockstats']['tcp'] = int(m.group(1))
                 else:
                      m = re.search(r"UDP: inuse (\d+)",line)
                      if m:
                           stats['sockstats']['udp'] = int(m.group(1))
                      else:
                           m = re.search(r"RAW: inuse (\d+)",line)
                           if m:
                                stats['sockstats']['raw'] = int(m.group(1))
                           else:
                                m = re.search(r"FRAG: inuse (\d+)",line)
                                if m:
                                     stats['sockstats']['ipfrag'] = int(m.group(1))

        f.close()

	return stats
		
		
if __name__ == "__main__":
   o = SockStats()
   print o.get_sock_stats()
	
