#!/usr/bin/env python

import sys, os, re

import rrdtool
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task

pref_port = 13023

class RRD(object):
    def clean_str(self, stat):
        # create a clean version of a string for RRDs, only alpha-num and underscore
        return re.sub('[^A-Za-z0-9]+', '_', str(stat))

    def map_name(self, stat):
        # map a stat name to a physical RRD file
        # TODO: create subdirectories based on stat or hash(stat) so we don't dump 10k RRDs in a single dir
        RRD_basepath = '/home/rmoore/stats/'
        return RRD_basepath + self.clean_str(stat) + '.rrd'

    def create(self, dsname):
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

        RRD_PARAMS = [ self.map_name(dsname), '--step', str(RRD_step), 'DS:' + self.clean_str(dsname) + ':GAUGE:12:0:U' ]

        for res, scale in zip(RRD_res, RRD_scale):
            step_res = res / RRD_step
            step_row = scale / res
            RRD_PARAMS.append('RRA:AVERAGE:0.99999:' + str(step_res) + ':' + str(step_row))

        result = apply(rrdtool.create, RRD_PARAMS)

    def update(self, stat, val):
        print "\tDumping stat %s value %s" % (stat, val)
        stat_file = self.map_name(stat)
        # need to create file, then we can update
        if not os.path.isfile(stat_file):
            print "\t__Creating RRD for %s__" % (stat)
            self.create(stat)
        rrdtool.update(stat_file, '--', 'N:' + str(val))


class Stats(object):
    def __init__(self):
        self.stats = {}
        self.RRD = RRD()

    def update(self, type, key, val):
        print "Updating %s with %s using %s" % (key, val, type)

        # count = 1 for SUM and AVG, but AVG will increment for each additional value
        increment = 1
        if not key in self.stats:
            # if we're creating this stat for the first time, set count == 1
            # once we do that, need to set increment == 0 so we don't count the first AVG value as 2 entries
            self.stats[key] = {'name':key, 'val':0, 'count':1}
            increment = 0
    
        if type == 'AVG':
            self.stats[key]['count'] += increment

        self.stats[key]['val'] += int(val)


    def dump(self):
        print "Dumping stats"
        # dump stats to RRDs
        for stat in self.stats:
            obj = self.stats[stat]
            self.RRD.update(obj['name'], obj['val'] / obj['count'])
        self.stats = {}
        print "Done dumping stats"


class StatServer(DatagramProtocol):

    def startProtocol(self):
        print "Starting stat_server"
        self.summarize = None
        self.statHolder = Stats()
        DatagramProtocol.startProtocol(self)

        # start stat dump
        self.summarize = task.LoopingCall(self.statHolder.dump)
        #self.summarize.start(10, now=False)
        self.summarize.start(10)

    def stopProtocol(self):
        print "Stopping stat_server:"
        DatagramProtocol.stopProtocol(self)
        print "\tStopping summary loop"
        self.summarize.stop()
        print "\tDumping accumulated stats"
        self.statHolder.dump()
        print "done"
        print ""

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
        data = data.strip()
        for line in data.splitlines():
            type, key, val = line.split()
            self.statHolder.update(type, key, val)

# remap output to stderr
sys.stdout = sys.stderr
reactor.listenUDP(pref_port, StatServer())
reactor.run()


