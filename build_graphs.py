import rrdtool

rrdtool.graph(outfile,
    '--start', 'now - 61 minute',
    '--end', 'now - 1 minute',
    'DEF:test_stat=test_rrd_9.rrd:test_rrd_9:AVERAGE',
    'CDEF:test_statx=test_stat,60,TREND',
    'AREA:test_statx#ff0000:"WTF"'
    '-h480', '-w640')

shell.exec('convert ' + outfile + ' bob.jpg')
shell.exec('display bob.jpg')

