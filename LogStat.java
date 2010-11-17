import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetSocketAddress;
import java.lang.RuntimeException;

final class LogStat {
    private static LogStat instance = null;

    // for testing:
    // private static String server_host = "10.40.40.101";
    private static String server_host = "127.0.0.1";
    private static int server_port = 13023;

    // singleton-esque variables
    private static StringBuffer buffer = null;
    private static DatagramSocket ds = null;
    private static InetSocketAddress sock_host = null;

    private LogStat() {
        this(server_host, server_port);
    }

    private LogStat(String host, int port) {
        server_host = host;
        server_port = port;
        try {
            if (ds == null) { ds = new DatagramSocket(); }
            if (buffer == null) { buffer = new StringBuffer(1024); }
            if (sock_host == null) { sock_host = new InetSocketAddress(server_host, server_port); }
        } catch (Exception e) { }
    }

    public static LogStat getInstance(String host, int port) throws RuntimeException {
        if (instance == null) {
            instance = new LogStat(host, port);
        } else {
            // if we're initializing for a second time with host/port, throw exception
            throw new RuntimeException("LogStat already initialized");
            // then keep going
        }
        return instance;
    }

    public static LogStat getInstance() {
        if (instance == null) {
            instance = new LogStat();
        }
        return instance;
    }

    // example: stat.log("key", 1, "SUM");
    public static void log(String key, int value, String type) {
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
        } catch (Exception e) { }
    }
    public static void log(String key, int value) { LogStat.getInstance().log(key, value, "SUM"); }
    public static void log(String key) { LogStat.getInstance().log(key, 1, "SUM"); }

    public synchronized static void log_s(String key, int value, String type) { LogStat.getInstance().log(key, value, type); }
    public synchronized static void log_s(String key, int value) { LogStat.getInstance().log(key, value); }
    public synchronized static void log_s(String key) { LogStat.getInstance().log(key); }
} 

