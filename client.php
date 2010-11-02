<?php
function logStat($statKey, $statVal = 1, $statType = 'SUM') {

    // TODO: parameterize this via configs
    $host_server = '127.0.0.1';
    $host_port = 13023;

    // 1 second connect timeout
    $conn = fsockopen('udp://' . $host_server, $host_port, $errno, $errstr, 1);
    if (!$conn) {
        // socket open error - since we're using UDP, this should never happen
        // UDP doesn't "open" a socket connection until data is written, it just allocates it
        return;
    }
    // 1 second sockwrite timeout
    stream_set_timeout($conn, 1);
    // strip tabs from key, any other character is valid
    $data = $statType . "\t" . str_replace("\t", "_", trim($statKey)) . "\t" . $statVal . "\n";
    fwrite($conn, $data);
    fclose($conn); 
}

/*
// for load testing:
$indexArray = array();
for($i = 0; $i < 100; $i++) $indexArray[$i] = 0;
$loopCount = 10000;
//mt_srand(42);
for ($i = 0; $i < $loopCount; $i++) {
    $index = mt_rand(0, 10);
    $val = mt_rand(1,100);
    $indexArray[$index] += $val;
    logStat('test_rrd_' . $index, $val);
}

$total = 0;
for($i = 0; $i < 100; $i++) $total += $indexArray[$i];
echo "Dumped $total values\n";
*/

