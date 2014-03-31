#!/usr/bin/env python
#
#############
# HDD stats
#############

import re
import os
import sys

"""DISK STATISTICS:
   major  -  The mayor number of the disk
   minor  -  The minor number of the disk
   rdreq  -  Number of read requests that were
             made to physical disk per second.
   rdbyt  -  Number of bytes that were read from
             physical disk per second.
   wrtreq -  Number of write requests that were
             made to physical disk per second.
   wrtbyt -  Number of bytes that were written
             to physical disk per second.
   ttreq  -  Total number of requests were made
             from/to physical disk per second.
   ttbyt  -  Total number of bytes transmitted
             from/to physical disk per secon.
	   	   
   USAGE:
   newObj = DiskStats()      ## Creates an object
   newObj.initialize()       ## Initialize statistics
   time.sleep(1)             ## Wait for a second
   newObj.get_disk_stats()   ## Gather statistics
"""

class DiskStats:
    """DiskStats class.	   
       Exported methods:
       initialize()
       get_disk_stats()
    """   
	   
    def __init__(self):
        """Constructor"""
        self.files = { }
        self.files['diskstats']  = '/proc/diskstats'
        self.files['partitions'] = '/proc/partitions'
        self.files['uptime']     = '/proc/uptime'
 
        ## The sectors are equivalent with blocks and have a size of 512
        self.blocksize = 512

    def initialize(self):
	"""Initialize statistics"""
        self.uptime = self._uptime()
        self.init   = self._load()


    def get_disk_stats(self):
	"""The main function.Gathers required statistics"""
        if not self.init:
            print "There are no initial statistics defined"
            sys.exit(1)

        self.stats = self._load()
        self._deltas()
        return self.stats

#
#  Private stuff 
#
    def _load(self, flag=None):
        file = self.files
        co   = re.compile(r"^\s+(\d+)\s+(\d+)\s+(.+?)\s+(\d+)\s+\d+\s+(\d+)\s+\d+\s+(\d+)\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+\d+$")
        
        try:
            f = open(file['diskstats'],"r")
        except IOError:
            flag = 1

        if flag == None: 
            for line in f:
                m = co.search(line)
                if m is not None:
                    blocks,device = m.group(3).split(' ')
                    stats = self._calc(device, int(blocks))
                else:
                    m = re.compile(r"^\s+(\d+)\s+(\d+)\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$")
                    for line in f:
                        m = co.search(line)
                        if  m is not None:
                            blocks,device = m.group(3).split(' ')
                            stats = self._calc(device, int(blocks))
        else: 
            try:
                f = open(file['partitions'],"r")
            except IOError :
                print "Couldn't open the file %s" % (file['partitions'])
              
            for line in f:
                m = co.search(line)
                if m is not None:
                    blocks,device = m.group(3).split(' ')
                    stats = self._calc(device, int(blocks) ,m)
                          
        if not file['diskstats'] or not stats:
            print "No diskstats found! your system seems not" 
            print "to be compiled with CONFIG_BLK_STATS=y"

        return stats

    def _deltas(self):
        """Creates a delta between the initial statistics and the final one"""
        istat       = self.init
        lstat       = self.stats
        uptime      = self._uptime()
        delta       = float(uptime) - float(self.uptime)
        self.uptime = uptime
       
        for dev in lstat.keys():
            if not istat.has_key(dev):
                del lstat[dev]
                continue
            idev = istat[dev]
            ldev = lstat[dev]

            for key,value in ldev.items():
                 if re.search(r'(^major\Z|^minor\Z)',key):
                     continue
            
                 if not idev.has_key(key):
                     print "Different keys in statistics"
                     sys.exit(1)
                 if not str(value).isdigit and \
                    not str(ldev[key]).isdigit():  
                     print "value of key is not a number"
                     sys.exit(1)
       
                 if ldev[key] == idev[key]:
                     ldev[key] = self._sprintf('%.2f', 0)
                 elif int(delta) > 0:
                     ldev[key] = self._sprintf('%.2f',float((ldev[key] - idev[key]) / delta))
                 else:
	             ldev[key] = self._sprintf('%.2f', float(ldev[key] - idev[key]))
                 idev[key] = value
        return idev


    def _uptime(self):
        """Finding uptime of the host"""
        file = self.files
        try:
           fd = open(file['uptime'],'r')
        except IOError:
           print "Couldn't open file['uptime'] file"
           sys.exit(1)
        up = fd.read().split(' ')[0]
        return up


    def _calc(self,device, blocks, m, stats={}):
        """Statistics calculation"""
        stats[device] = { }
        stats[device]['blocks'] = blocks
        stats[device]['major']  = int(m.group(4))
        stats[device]['minor']  = int(m.group(2))
        stats[device]['rdreq']  = int(m.group(4))
        stats[device]['rdbyt']  = int(m.group(5)) * self.blocksize
        stats[device]['wrtreq'] = int(m.group(6))
        stats[device]['wrtbyt'] = int(m.group(7)) * self.blocksize
        ttreq  = stats[device]['rdreq'] + stats[device]['rdreq']
        ttbyt  = stats[device]['rdbyt'] + stats[device]['wrtbyt']
        stats[device]['ttreq'] = ttreq + stats[device]['rdreq'] + stats[device]['wrtreq']
        stats[device]['ttbyt'] = ttbyt + stats[device]['rdbyt'] + stats[device]['wrtbyt']
        return stats

    
    def _sprintf(self,format,*args):
        """String formatting""" 
        return format % (args)


if __name__ == '__main__':
   ds = DiskStats()
   ds.initialize()
   #import time
   #time.sleep(5)
   print ds.get_disk_stats()


