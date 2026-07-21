package io.meterhub.app;

public final class Main {
    private Main() {}

    public static void main(String[] args) {
        String summary = MeterCore.ingest(new String[] {"s1", "s2", "s3"});
        int legacy = LegacyImport.importLegacy("a;b;c");
        System.out.println("SUMMARY " + summary + " legacy=" + legacy);
    }
}
