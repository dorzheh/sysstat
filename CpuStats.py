#!/usr/bin/env python
#
#############
#  CPU stats
#############


"""CPU STATISTICS:
   user    -  Percentage of CPU utilization at the user level.    
   nice    -  Percentage of CPU utilization at the user level
              with nice priority.
   system  -  Percentage of CPU utilization at the system level.
   idle    -  Percentage of time the CPU is in idle state.
   iowait  -  Percentage of time the CPU is in idle state because
              an i/o operation is waiting for a disk.
              This statistic is only available by kernel versions
              higher than 2.4. Otherwise this statistic
              exists but will be ever 0.
   total   -  Total percentage of CPU utilization (user + nice + system).
   
   
   
   USAGE:
   newObj = CpuStats.CpuStats() ## Creates an object
   newObj.initialize()          ## Initialize statistics
   time.sleep(1)                ## Wait for a second
   newObj.get_cpu_stats()       ## Gather statistics
"""
   
import re
import sys
  
class CpuStats:

    """Cpu class.
       Exported methods:
       initialize()
       get_cpu_stats()		
    """
	
    def __init__(self):
	"""Constructor"""
        self.files = { }
        self.files['stat'] = '/proc/stat'
        self.keys =('user','nice','system','idle',
                   'iowait','irq','softirq')

    def initialize(self):
        """Initializes statistics"""
        self.init = self._load()

    def get_cpu_stats(self):
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
    def _load(self,stats={}):
        file = self.files
        expr = re.compile("^(cpu.*?)\s+(.*)$")
        try:
            f = open(file['stat'],'r')
        except IOError:
            print "Cannot open the file %s" % (file['stat'])
            sys.exit(1)

        for line in f:
            m = expr.search(line)
            if m:
                stats[m.group(1)] = dict(zip(self.keys,m.group(2).split(' ')))
        return stats
    

    def _deltas(self,uptime=0,istat={},lstat={}):
        """Creates a delta between init state and 
           statistics gathered later"""
        istat = self.init
        lstat = self.stats

        for cpu in lstat.keys():
            icpu = istat[cpu]
            dcpu = lstat[cpu]

            for key,value in dcpu.items():
                if not icpu[key]:
                    print "No value for the key %s" % (key)
                    sys.exit(1)

                if not str(value).isdigit() and \
                    not str(dcpu[key]).isdigit():
                    print "Value of 'key' is not a number"
                    sys.exit(1)
                dcpu[key]  = int(dcpu[key])
                dcpu[key] -= int(icpu[key])
                icpu[key]  = value
                uptime += int(dcpu[key])

            for key in dcpu.keys():
                if dcpu[key] > 0:
                    dcpu[key] = self._sprintf('%.2f', 100 * int(dcpu[key]) / uptime)
                else:
                    dcpu[key] = self._sprintf('%.2f', dcpu[key])
        
            dcpu['total'] = self._sprintf('%.2f', float(dcpu['user']) + float(dcpu['nice']) + float(dcpu['system']))
	    if dcpu.has_key('irq'):
                del dcpu['irq']

            if dcpu.has_key('softirq'):		   
                del dcpu['softirq'] 

     
    def _sprintf(self, format, *args):
        """String formatting"""
        return format % args 


if __name__ == '__main__':
  obj = CpuStats()
  obj.initialize()
  print obj.get_cpu_stats()
