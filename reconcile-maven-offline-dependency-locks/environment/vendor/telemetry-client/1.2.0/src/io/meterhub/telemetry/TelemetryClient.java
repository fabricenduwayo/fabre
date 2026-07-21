package io.meterhub.telemetry;

import io.meterhub.wire.Frame;

public final class TelemetryClient {
    private int count;

    private TelemetryClient() {}

    public static TelemetryClient open() {
        return new TelemetryClient();
    }

    public TelemetryClient record(String sample) {
        Frame.encode(sample);
        count++;
        return this;
    }

    public String summary() {
        return "count=" + count + " wire=" + Frame.version();
    }
}
