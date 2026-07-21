package io.meterhub.wire;

public final class Frame {
    private Frame() {}

    public static String encodeFrame(String payload) {
        return "F3[" + payload + "]";
    }

    public static String decodeFrame(String frame) {
        return frame.substring(3, frame.length() - 1);
    }

    public static String version() {
        return "3.0.0";
    }
}
