package io.meterhub.telemetry;

import io.meterhub.wire.Frame;

public final class TelemetryClient {
    private int count;
    private int pending;

    private TelemetryClient() {}

    public static TelemetryClient open() {
        return new TelemetryClient();
    }

    public TelemetryClient record(String sample) {
        Frame.encode(sample);
        count++;
        pending++;
        return this;
    }

    public String flushBatch() {
        String batch = Frame.encode("batch:" + pending);
        pending = 0;
        return batch;
    }

    public String summary() {
        return "count=" + count + " wire=" + Frame.version();
    }
}
