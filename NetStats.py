#!/usr/bin/env python
#
############
# netstats
############

"""NETWORK STATISTICS: 
   rxbyt    -  Number of bytes received per second.
   rxpcks   -  Number of packets received per second.
   rxerrs   -  Number of errors that happend while
               received packets per second.
   rxdrop   -  Number of packets that were dropped per second.
   rxfifo   -  Number of FIFO overruns that happend on
               received packets per second.
   rxframe  -  Number of carrier errors that happend on 
               received packets per second.
   rxcompr  -  Number of compressed packets received per second.
   rxmulti  -  Number of multicast packets received per second.
   txbyt    -  Number of bytes transmitted per second.
   txpcks   -  Number of packets transmitted per second.
   txerrs   -  Number of errors that happend while transmitting
               packets per second.
   txdrop   -  Number of packets that were dropped per second.
   txfifo   -  Number of FIFO overruns that happend on transmitted
               packets per second.
   txcolls  -  Number of collisions that were detected per second.
   txcarr   -  Number of carrier errors that happend on
               transmitted packets per second.
   txcompr  -  Number of compressed packets transmitted per second.
   ttpcks   -  Number of total packets (received + transmitted) per second.
   ttbyt    -  Number of total bytes (received + transmitted) per second.

   USAGE:
   newObj = NetStats()    ## Creates an object
   newObj.initialize()    ## Initialize the statistics
   time.sleep(1)          ## Wait for a second
   newObj.get_net_stats() ## Gather statistics
"""

import re
import sys

class NetStats:

    """NetStats class.
       Exported methods:
       initialize()
       get_net_stats()	   
    """
	
    def __init__(self):
	"""Constructor"""
        self.files = {'netstats' : '/proc/net/dev',
                      'uptime'   : '/proc/uptime' }
          
        self.list  = ('rxbyt','rxpcks','rxerrs','rxdrop',
                      'rxfifo','rxframe','rxcompr','rxmulti',
                      'txbyt', 'txpcks', 'txerrs', 'txdrop',
                      'txfifo', 'txcolls', 'txcarr', 'txcompr')

    def initialize(self):
	"""Initializes statistics"""
        self.uptime = self._uptime()
        self.init   = self._load()

    def get_net_stats(self):
	"""The main function.Gethers required statistics"""

        if not self.init:
            print "there are no initial statistics defined"
            sys.exit(1)

        self.stats = self._load()
        self._deltas()

        return self.stats

#
# Private stuff
#
    def _load(self,stats={},line=[]):

        file = self.files
        try:
            f = open(file['netstats'],'r')
        except IOError:
            print "Couldn't open the file %s" % (file['netstats'])
            sys.exit(1)

        cmpldexpr = re.compile(r'^\s*(\w+):\s*(.*)')
        splexpr   = re.compile(r'\s+')
        for line in f:
            m = cmpldexpr.search(line)
            if not m:
                continue
            lines = map(int,splexpr.split(m.group(2))) 
            stats[m.group(1)] = dict(zip(self.list,lines))
            stats[m.group(1)]['ttbyt']  = stats[m.group(1)]['rxbyt']  + stats[m.group(1)]['txbyt']
            stats[m.group(1)]['ttpcks'] = stats[m.group(1)]['rxpcks'] + stats[m.group(1)]['txpcks']
        
        return stats


    def _deltas(self):

        istat       = self.init
        lstat       = self.stats
        uptime      = float(self._uptime())
        delta       = uptime - float(self.uptime)
        self.uptime = uptime

        for dev in lstat.keys():
            if not istat[dev]:
                del lstat[dev]
                continue 
            idev = istat[dev]
            ldev = lstat[dev]

            for key, value in ldev.items():
                 if not idev.has_key(key):
                     print "Different keys in statistics"
                     sys.exit(1)

                 if not str(value).isdigit() and \
                    not str(idev[key]).isdigit():
                    print "Value of 'key' is not a number"
                    sys.exit(1)

                 if ldev[key] == idev[key]:
                     ldev[key] = self._sprintf('%.2f', 0)
                 elif delta > 0:
                     ldev[key] = (ldev[key] - idev[key]) / delta
                 else:
                     ldev[key] = ldev[key] - idev[key]
                 idev[key] = value

        return idev


    def _uptime(self):

        file  = self.files

        try:
            f = open(file['uptime'],'r')
        except IOError:
            print "Couldn't open the file %s" % (file['uptime'])
            sys.exit(1)
              
        up = f.read().split(' ')[0]
        return up
 

    def _sprintf(self, format,*args):
        return format % (args)


if __name__ == "__main__":
   obj = NetStats()
   obj.initialize()
   import time
   time.sleep(2)
   print obj.get_net_stats()
