#!/usr/bin/env python

import sys, os, re, time
import rrdtool
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol

pref_port = 13023

# helper function
# TODO: don't be this guy
def log(str):
    sys.stderr.write(time.strftime("[%Y/%m/%d:%H:%M:%S] ", time.localtime()) + str + "\n")

class RRD(object):
    def clean_str(self, stat):
        # create a clean version of a string for RRDs, only alpha-num and underscore
        return re.sub('[^A-Za-z0-9_]+', '_', str(stat))

    def map_name(self, stat):
        # map a stat name to a physical RRD file
        # TODO: create subdirectories based on stat or hash(stat) so we don't dump 10k RRDs in a single dir
        RRD_basepath = '/var/stats/'
        return RRD_basepath + self.clean_str(stat) + '.rrd'

    def create(self, dsname):
        # default step size in seconds
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
        log("\tDumping stat %s value %s" % (stat, val))
        stat_file = self.map_name(stat)
        # need to create file, then we can update
        if not os.path.isfile(stat_file):
            log("\t\tCreating RRD for %s" % (stat))
            self.create(stat)
            # meta stat - how many new stat files we created
            self.update('rrd_file_created', 1)
        rrdtool.update(stat_file, '--', 'N:' + str(val))


class Stats(object):
    def __init__(self):
        self.stats = {}
        self.RRD = RRD()

    def update(self, type, key, val):
        # debug (logs way WAY too much)
        # log("Updating %s with %s using %s" % (key, val, type))

        # count = 1 for SUM and AVG, but AVG will increment for each additional value
        increment = 1
        if not key in self.stats:
            # if we're creating this stat for the first time, set count == 1
            # once we do that, need to set increment == 0 so we don't count the first AVG value as 2 entries
            self.stats[key] = {'name':key, 'val':0.0, 'count':1}
            increment = 0

        if type == 'AVG':
            self.stats[key]['count'] += increment

        self.stats[key]['val'] += float(val)

    def dump(self):
        log("Dumping stats")
        # dump stats to RRDs
        for stat in self.stats:
            obj = self.stats[stat]
            self.RRD.update(obj['name'], obj['val'] / obj['count'])
        self.stats = {}
        log("Done dumping stats")


class StatServer(DatagramProtocol):

    def startProtocol(self):
        log("Starting stat_server")
        self.summarize = None
        self.statHolder = Stats()
        DatagramProtocol.startProtocol(self)

        # start stat dump collector task
        self.summarize = task.LoopingCall(self.statHolder.dump)
        self.summarize.start(10, now=False)

    def stopProtocol(self):
        # clean shutdown has to happen like:
        #  - stop accepting new packets
        #  - stop our loop to dump stats
        #  - manually dump any remaining stats
        log("Stopping stat_server:")
        DatagramProtocol.stopProtocol(self)
        log("\tStopping summary loop")
        self.summarize.stop()
        log("\tDumping accumulated stats")
        self.statHolder.dump()
        log("Stopped stat_server")

    def datagramReceived(self, data, (host, port)):
        # debug (logs way too much)
        # log("received %r from %s:%d" % (data, host, port))
        data = data.strip()
        # meta stat - how many packets we got
        self.statHolder.update('SUM', 'rrd_stat_packets', 1)
        for line in data.splitlines():
            type, key, val = line.split()
            self.statHolder.update(type, key, val)
            # meta stat - how many individual stats we got
            self.statHolder.update('SUM', 'rrd_stat_updates', 1)

reactor.listenUDP(pref_port, StatServer())
reactor.run()

