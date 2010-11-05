
class TestDriver{
    public static void main(String args[]) {
        System.out.println("Sending packets");
        for (int i = 0; i < 10; i++) {
            LogStat.stat("key", 1, "SUM");
        }
        System.out.println("Completed");
    }
 }
