import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

class LogStat {
    private static DatagramSocket ds = null;
    private static StringBuffer buffer = null;
    private static int server_port = 13023;
    // private static String server_host = "127.0.0.1";
    private static String server_host = "10.40.40.101";
    private static InetAddress in_host = null;

    private static void InitVars() {
        // default to 64-byte packet, tweak this as necessary to avoid reallocations
        if (buffer == null) { buffer = new StringBuffer(64); }
        if (ds == null) { ds = new DatagramSocket(server_port); }
        if (in_host == null) { in_host = InetAddress.getByName(server_host); }
        buffer.setLength(0);
    }

    // example: LogStat.stat("key", 1, "SUM");
    public static void stat(String key, int value, String type) {
        // only allocate one socket and one stringbuffer
        InitVars();

        try {
            buffer.append(type);
            buffer.append("\t");
            buffer.append(key);
            buffer.append("\t");
            buffer.append(Integer.toString(value));
            buffer.append("\n");

            byte [] output = buffer.toString().getBytes();
            DatagramPacket packet = new DatagramPacket(output, output.length, in_host, server_port);
            ds.send(packet);
        } catch (Exception e) {
        }
    }
    public static void stat(String key, int value) { LogStat.stat(key, value, "SUM"); }
    public static void stat(String key) { LogStat.stat(key, 1, "SUM"); }
} 

