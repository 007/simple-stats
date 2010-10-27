<?php
function logStat($statKey, $statVal = 1, $statType = 'SUM') {

    $host_server = '127.0.0.1';
    $host_port = 13023;

    // 10 second connect timeout
    $conn = fsockopen('udp://' . $host_server, $host_port, $errno, $errstr, 10);
    if (!$conn) {
        // socket open error
        // since we're using UDP, this should never happen;
        // UDP doesn't "open" a socket connection until data is written, it just allocates it
        return;
    }
    // 10 second sockwrite timeout
    stream_set_timeout($conn, 10);
    // strip tabs from key, any other character is valid
    $data = $statType . "\t" . str_replace("\t", "_", trim($statKey)) . "\t" . $statVal . "\n";
    fwrite($conn, $data);
    fclose($conn); 
}


$prodArray = array("product1", "product2");
logStat("products_sold", count($prodArray));
foreach($prodArray as $key=>$val) {
    logStat("product_" . $val, 1);
}
logStat("key");
logStat("key2");
logStat("key3", 10);


