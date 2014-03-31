#!/usr/bin/env python
#
############
# Sysinfo
############

"""SYSTEM STATISTICS:
   hostname  -  This is the host name.
   domain    -  This is the host domain name.
   kernel    -  This is the kernel name.
   release   -  This is the release number.
   version   -  This is the version number.
   memtotal  -  The total size of memory.
   swaptotal -  The total size of swap space.
   countcpus -  The total (maybe logical) number of CPUs.
   uptime    -  This is the uptime of the system.
   idletime  -  This is the idle time of the system.
	
   USAGE:
   newObj = SysInfo()    ## Creates an object       
   newObj.get_sys_info() ## Gather statistics
"""	
	
import re
import sys


class SysInfo: 
    """SysInfo calss.
       Exported methods:
       get_sys_info()	 
    """

    def __init__(self):
	"""Constructor"""
        self.files = {'meminfo'  : '/proc/meminfo',
                      'sysinfo'  : '/proc/sysinfo',
                      'cpuinfo'  : '/proc/cpuinfo',
                      'uptime'   : '/proc/uptime',
                      'hostname' : '/proc/sys/kernel/hostname',
                      'domain'   : '/proc/sys/kernel/domainname',
                      'kernel'   : '/proc/sys/kernel/ostype',
                      'release'  : '/proc/sys/kernel/osrelease',
                      'version'  : '/proc/sys/kernel/version' }

    def get_sys_info(self,stats={}):
        """Gathers system information"""
        file  = self.files
        stats['sysinfo']  = {}

        for pfile in ('hostname', 'domain', 'kernel',
                      'release', 'version'):
            try:
                f = open(file[pfile])
            except IOError:
                print "unable to open file %s" % (file[pfile])
                sys.exit(1)

            stats['sysinfo'][pfile] = f.read().strip()
            f.close()

        try:
            f = open(file['meminfo'],"r")
        except IOError:
            print "Unable to open file %s" % (file['meminfo'])
            sys.exit(1)

        cmpld = re.compile("^MemTotal:\s+(\d+ \w+)")
        for line in f:
            m = cmpld.search(line)
            if m:
                stats['sysinfo']['memtotal'] = m.group(1)
            else:
                cmpld = re.compile("^SwapTotal:\s+(\d+ \w+)")
                m = cmpld.search(line)
                if m:
                    stats['sysinfo']['swaptotal'] = m.group(1)

        f.close()

        ## Setting the total amount of CPUs on the system to 0
        stats['sysinfo']['countcpus'] = 0

        try:
            f = open(file['cpuinfo'],"r")
        except IOError: 
            print "unable to open file %s" % (file['cpuinfo'])
            sys.exit(1)

        cmpld = re.compile(r"^processor\s*:\s*\d+")
        for line in f:
            if cmpld.search(line):
                stats['sysinfo']['countcpus'] += 1
            else:
                cmpld = re.compile(r"^# processors\s*:\s*(\d+)")
                m = cmpld.search(line)
                if m:
                    stats['sysinfo']['countcpus'] = m.group(1)
                    break
        f.close()

        try:
            f = open(file['uptime'],"r")
        except IOError:
            print "unable to open file %s" % (file['uptime'])
            sys.exit(1)

        for seconds in f.read().split(' '):
            d, h, m, s = self._calsec(seconds)
            if not stats.has_key('uptime'):
                string = str(d) + 'd' + ' ' + str(h) + 'h' + \
		         ' ' + str(m) + 'm' + ' ' + str(s) + 's'
                stats['sysinfo']['uptime'] = string.split(' ')
                continue
        string = str(d) + 'd' + ' ' + str(h) + 'h' + ' ' +\
                 str(m) + 'm' + ' ' + str(s) + 's'
 
        stats['sysinfo']['idletime'] =  string.split(' ')

        return stats

#
# Private stuff
#
    def _calsec(self, sec, min=0, hour=0, day=0):
	"""Parsing argument(seconds)"""
        sec = float(sec)
        if sec >= 86400:
            day = sec / 86400
            sec = sec % 86400

        if sec >= 3600:
            hour = sec / 3600
            sec  = sec % 3600

        if sec >= 60:
            min = sec / 60
            sec = sec % 60
        
        hour = self._sprintf("%.2f",hour)
        min  = self._sprintf("%.2f",min)
        sec  = self._sprintf("%.2f",sec)

        return day, hour, min, sec


    def _sprintf(self,format,*args):
        """String formatting"""
        return format % (args)


if __name__ == "__main__":
   obj = SysInfo()
   print obj.get_sys_info()
