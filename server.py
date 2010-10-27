#!/usr/bin/env python

import os, re

import rrdtool
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task

pref_port = 13023

class RRD(object):
    def clean_str(stat):
        # create a clean version of a string for RRDs, only alpha-num and underscore
        return re.sub('[^A-Za-z0-9]+', '_', str(stat))

    def map_name(stat):
        # map a stat name to a physical RRD file
        # TODO: create subdirectories based on stat or hash(stat) so we don't dump 10k RRDs in a single dir
        RRD_basepath = '/home/rmoore/stats/'
        return RRD_basepath + self.clean_str(stat) + '.rrd'

    def create(dsname):
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

    @staticmethod
    def update(stat, val):
        stat_file = self.map_name(stat)
        # need to create file, then we can update
        if not os.path.isfile(statfile):
            self.create(stat)
        rrdtool.update(stat_file, '--', 'N:' + str(val))


class Stats(object):
    stats = {}

    @staticmethod
    def update(type, key, val):
        print "Updating %s with %s using %s" % (key, value, type)

        # count = 1 for SUM and AVG, but AVG will increment for each additional value
        increment = 1
        if not key in stats:
            # if we're creating this stat for the first time, set count == 1
            # once we do that, need to set increment == 0 so we don't count the first AVG value as 2 entries
            stats[key] = {'name':key, 'val':0, 'count':1}
            increment = 0
    
        if type == 'AVG':
            stats[key]['count'] += increment

        stats[key]['val'] += val


    @staticmethod
    def dump():
        print "__dumping stats"
        # dump stats to RRDs
        # pop each element out of dict as we process, that will clean out list as we dump stats
        while stats:
            stat = stats.pop()
            RRD.update(stat['name'], stat['val'] / stat['count'])
        print "__done"


class StatServer(DatagramProtocol):

    def startProtocol(self):
        print "Starting stat_server"
        self.summarize = None
        DatagramProtocol.startProtocol(self)

        # start stat dump
        self.summarize = task.LoopingCall(Stats.dump)
        self.summarize.start(5, now=False)

    def stopProtocol(self):
        print "Stopping stat_server:"
        DatagramProtocol.stopProtocol(self)
        print "\tStopping summary loop"
        self.summarize.stop()
        print "\tDumping accumulated stats"
        Stats.dump()
        print "done"
        print ""

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
        data = data.strip()
        for line in data.splitlines():
            type, key, val = line.split()
            Stat.update(type, key, val)

reactor.listenUDP(pref_port, StatServer())
reactor.run()


