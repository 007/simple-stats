#!/usr/bin/env python

import rrdtool
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

pref_port = 13023


def create_rrd(fname, dsname):
    # where to store RRDs
    RRD_basepath = '/home/rmoore/stats/'
 
    # default step size, 10-second resolution
    RRD_step = 10

    # default ranges to keep in our RRD:
    # 24 hours of 10-second average
    # 10 days of 1-minute average
    # 40 days of 1-hour average
    # 1 year of 1-day average
    # 10 years of 10-day average

    # time scale: 1 day, 10 days, 40 days,   1 year, 10 years (in seconds)
    RRD_scale = [ 86400,  864000, 3456000, 31622400, 315576000 ]

    # resolution: 10 second, 1 minute, 1 hour, 1 day, 10 day (in seconds) 
    RRD_res = [          10,       60  , 3600, 86400, 864000 ]

    # explict str cast for fname and dsname, in case they're INT from input
    RRD_PARAMS = [ RRD_basepath + str(fname) + '.rrd', '--step', str(RRD_step), 'DS:' + str(dsname) + ':GAUGE:12:0:U' ]
    # TODO: create subdirectories based on fname or hash(fname) so we don't dump 10k RRDs in a single dir

    for res, scale in zip(RRD_res, RRD_scale):
        step_res = res / RRD_step
        step_row = scale / res
        RRD_PARAMS.append('RRA:AVERAGE:0.99999:' + str(step_res) + ':' + str(step_row))

    result = apply(rrdtool.create, RRD_PARAMS)


# example: create_rrd('hits', 'apache_hits') to create hits.rrd containing apache_hits as a data source

class StatServer(DatagramProtocol):
    def __init__(self, core):
        """Note: Parent class has no __init__ to call"""
        self.rollup_task = None
        self.stats = {}
        self.core = core

    def updateState(type, key, value):
        print "Updating %s with %s using %s" % (key, value, type)

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
        data = data.strip()
        for line in data.splitlines():
            type, key, val = line.split()
            Stat.update(type, key, val)


reactor.listenUDP(pref_port, StatServer())
reactor.run










 
class ReflexProtocol(protocol.DatagramProtocol):

    def __init__(self, core):
        """Note: Parent class has no __init__ to call"""
        self.rollup_task = None
        self.stats = {}
        self.core = core

    def datagramReceived(self, data, (host, port)):
        data = data.strip()
        for line in data.splitlines():
            key, val, type = line.split()
            stat = self.getStat(type, key)
            if stat:
                stat.update(val)

    def getStat(self, type, key):
        full_key = "%s_%s" % (type, key)
        type = int(type)

        if full_key not in self.stats:
            # TODO: Switch to dynamic dispatch or something
            if type == stats.TYPE_SUM:
                self.stats[full_key] = stats.SumStat(self.core, key)
            elif type == stats.TYPE_AVERAGE:
                self.stats[full_key] = stats.AverageStat(self.core, key)
            else:
                log.msg('Unknown stat type: %s' % type)
                return None

        return self.stats[full_key]

    def startProtocol(self):
        protocol.DatagramProtocol.startProtocol(self)

        # start data rollup task
        self.rollup_task = task.LoopingCall(self.rollupData)
        self.rollup_task.start(60, now=False)

    def stopProtocol(self):
        protocol.DatagramProtocol.stopProtocol(self)

    def rollupData(self):
        for stat in self.stats:
            self.stats[stat].rollup()



