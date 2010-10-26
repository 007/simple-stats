#!/usr/bin/env python

import os, re

import rrdtool
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

pref_port = 13023


class RRD(object):
    def clean_str(stat):
        # create a clean version of a string for RRDs, only alpha-num and underscore
        return re.sub('[^A-Za-z0-9]+', '_', str(stat))

    def map_name(stat):
        # map a stat name to a physical RRD file
        # TODO: create subdirectories based on fname or hash(fname) so we don't dump 10k RRDs in a single dir
        RRD_basepath = '/home/rmoore/stats/'
        return RRD_basepath + self.clean_str(stat) + '.rrd'

    # example: create('hits', 'apache_hits') to create hits.rrd containing apache_hits as a data source
    def create(fname, dsname):
        # where to store RRDs
     
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

        RRD_PARAMS = [ self.map_name(fname), '--step', str(RRD_step), 'DS:' + self.clean_str(dsname) + ':GAUGE:12:0:U' ]

        for res, scale in zip(RRD_res, RRD_scale):
            step_res = res / RRD_step
            step_row = scale / res
            RRD_PARAMS.append('RRA:AVERAGE:0.99999:' + str(step_res) + ':' + str(step_row))

        result = apply(rrdtool.create, RRD_PARAMS)

    def update(stat, val):
        stat_file = self.map_name(stat)
        if !os.path.isfile(statfile):
            # need to create file, then we can update
            self.create(stat, stat)
        # TODO: fix this
        rrdtool.update(stat_file, stat, val)

class Stats(object):
    def update(type, key, val):
        # TODO: update these to actually work
        if !type in self.stats:
            self.stats[type] = {}
        if !key in self.stats[type]:
            self.stats[type][key] = 0;
        # update a stat, internally
        self.stats[type][key] += val

    def dump():
        # dump stats to RRDs
        for stat, val in self.stats
            RRD.update(stat, val)


class StatServer(DatagramProtocol):
    def __init__(self, core):
        """Note: Parent class has no __init__ to call"""
        self.summarize = None
        self.stats = {}
        self.core = core

    def startProtocol(self):
        protocol.DatagramProtocol.startProtocol(self)

        # start stat dump
        self.summarize = task.LoopingCall(self.dumpStats)
        self.summarize.start(10, now=False)

    def stopProtocol(self):
        protocol.DatagramProtocol.stopProtocol(self)


    def updateState(type, key, value):
        print "Updating %s with %s using %s" % (key, value, type)

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
        data = data.strip()
        for line in data.splitlines():
            type, key, val = line.split()
            Stat.update(type, key, val)

    def dumpStats():
        for statName, statVal in self.stats


reactor.listenUDP(pref_port, StatServer())
reactor.run










 
class ReflexProtocol(protocol.DatagramProtocol):


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

    def rollupData(self):
        for stat in self.stats:
            self.stats[stat].rollup()



