#!/usr/bin/env python
#
###########################
# Sysusage info:
#  1)  memory/swap usage
#  2)  disk usage
#  3)  load avarage
###########################

import re
import os

class MemoryUsage:
    """MEMORY USAGE STATISTICS:
       memused      -  Total size of used memory in kilobytes.
       memfree      -  Total size of free memory in kilobytes.
       memusedper   -  Total size of used memory in percent.
       memtotal     -  Total size of memory in kilobytes.
       buffers      -  Total size of buffers used from memory in kilobytes.
       cached       -  Total size of cached memory in kilobytes.
       realfree     -  Total size of memory is real free
                       (memfree + buffers + cached).
       realfreeper  -  Total size of memory is real free in
                       percent of total memory.
       swapused     -  Total size of swap space is used is kilobytes.
       swapfree     -  Total size of swap space is free in kilobytes.
       swapusedper  -  Total size of swap space is used in percent.
       swaptotal    -  Total size of swap space in kilobytes.

       The following statistics are only available by kernels from 2.6.
		
       slab         -  Total size of memory in kilobytes that used by
                       kernel for the data structure allocations.
       dirty        -  Total size of memory pages in kilobytes that
                       waits to be written back to disk.
       mapped       -  Total size of memory in kilbytes that is mapped
                       by devices or libraries with mmap.
       writeback    -  Total size of memory that was written back to disk.
 
       USAGE:
       newObj = SysUsage.MemoryUsage() ## Creates an object
       newObj.get_mem_usage() ## Gather statistics
       """	
	
    def __init__(self):
	"""Constructor"""
        self.meminfo = { }
        file = '/proc/meminfo'
        expr = re.compile(r'^(MemTotal|MemFree|Buffers|Cached|SwapTotal|SwapFree|Slab|Dirty|Mapped|Writeback):\s*(\d+)')
        for line in open(file,"r"):
            m = expr.search(line)
            if m: 
                self.meminfo[m.group(1).lower()] = int(m.group(2))

    def get_mem_usage(self):
        """The main function."""
        output = self.meminfo
        output['memused']     = int(output['memtotal'] - output['memfree'])
        output['memusedper']  = int(100 * output['memused'] / output['memtotal'])
        output['swapused']    = int(output['swaptotal'] - output['swapfree'])
        output['realfree']    = int(output['memfree'] + output['buffers'] + output['cached'])
        output['realfreeper'] = int(100 * output['realfree'] / output['memtotal'])
        # In case no swap space on the machine
        if not output['swaptotal']:
            output['swapusedper'] = 0
        else: 
            output['swapusedper'] = int(100 * output['swapused'] / output['swaptotal'])
        return output
   
   
class DiskUsage:
    """DiskUsage class.
       Exported methods:
       disk_usage()
	   
       DISK USAGE STATISTICS:
       total      -  The total size of the disk.
       usage      -  The used disk space in kilobytes.
       free       -  The free disk space in kilobytes.
       usageper   -  The used disk space in percent.
       mountpoint -  The moint point of the disk.
	   
       USAGE:
       newObj = SysUsage.DiskUsage() ## Creates an object.
       newObj.disk_usage()           ## Gather statistics
    """   

    def __init__(self,cmd=None):
	"""Constructor"""
        if cmd == None:
             self.cmd = '/bin/df'
        else:
             self.cmd =  cmd 

        self.stats = {}
        self.stats['diskusage'] = {}

    def get_disk_usage(self):
	"""The main function.Gathers disk usage information"""
        p = os.popen(self.cmd)
        for line in p.readlines():
            m = re.search(r'(\d+)\%\s+(.+)$',line)
            if m:
                self.stats['diskusage'][m.group(2)] = int(m.group(1))
        return self.stats


class LoadAVG:
     """LoadAVG class.
        Exported methods:
        get_load_avg()
	   
	LOAD AVARAGE STATISTICS:
        avg_1   -  The average processor workload 
                   of the last minute.
        avg_5   -  The average processor workload
                   of the last five minutes.
        avg_15  -  The average processor workload
                   of the last fifteen minutes.
        USAGE:
        newObj = LoadAVG()     ## Creates an object
        newObj.get_load_avg()  ## Gather statistics
     """
	
     def __init__(self):
	"""Constructor"""
        self.file  = '/proc/loadavg'
        self.tuple = ('avg_1','avg_5','avg_15')
        self.elems = []
        self.stats = {}

     def get_load_avg(self):
	"""The main function.Gathers load avarage statistics"""
        try:
            f = open(self.file,'r')
        except IOError:
            print "Unable to open the file %s" % (self.file)
            sys.exit(1)
        self.stats['load_avarage'] = {}

        for x in map(float,f.read().split(" ")[0:3]):
             x = self._format("%.2f",x)
             self.elems.append(x)

        self.stats['load_avarage'] = dict(zip(self.tuple,self.elems))
        return self.stats

     def _format(self,format, *arg):
         return format % (arg)


if __name__ == '__main__':
   o = LoadAVG()
   print  o.get_load_avg()
   m = MemoryUsage()
   usage = m.get_mem_usage()
   print usage
   du = DiskUsage()
   print du.get_disk_usage()
