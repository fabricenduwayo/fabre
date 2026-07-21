package io.meterhub.wire;

public final class Frame {
    private Frame() {}

    public static String encode(String payload) {
        return "F[" + payload + "]";
    }

    public static String decode(String frame) {
        return frame.substring(2, frame.length() - 1);
    }

    public static String version() {
        return "2.3.0";
    }
}
