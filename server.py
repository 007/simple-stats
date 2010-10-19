#!/bin/env python
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

pref_port = 13023

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



