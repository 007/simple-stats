import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetSocketAddress;

class LogStat {
    // for testing:
    // private static String server_host = "10.40.40.101";
    private static String server_host = "127.0.0.1";
    private static int server_port = 13023;

    // singleton-esque variables
    private static StringBuffer buffer = null;
    private static DatagramSocket ds = null;
    private static InetSocketAddress sock_host = null;

    static {
        try {
            if (buffer == null) { buffer = new StringBuffer(1024); }
            if (ds == null) { ds = new DatagramSocket(); }
            if (sock_host == null) { sock_host = new InetSocketAddress(server_host, server_port); }
        } catch (Exception e) {
        }
    }

    // example: LogStat.stat("key", 1, "SUM");
    public synchronized static void stat(String key, int value, String type) {
        try {
            buffer.setLength(0);
            buffer.append(type);
            buffer.append("\t");
            buffer.append(key);
            buffer.append("\t");
            buffer.append(Integer.toString(value));
            buffer.append("\n");

            byte [] output = buffer.toString().getBytes();
            DatagramPacket packet = new DatagramPacket(output, output.length, sock_host);
            ds.send(packet);
        } catch (Exception e) {
        }
    }
    public static void stat(String key, int value) { LogStat.stat(key, value, "SUM"); }
    public static void stat(String key) { LogStat.stat(key, 1, "SUM"); }
} 
