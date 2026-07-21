package io.meterhub.app;

import io.meterhub.telemetry.TelemetryClient;

public final class MeterCore {
    private MeterCore() {}

    public static String ingest(String[] samples) {
        TelemetryClient client = TelemetryClient.open();
        for (String sample : samples) {
            client.record(sample);
        }
        client.flushBatch();
        return client.summary();
    }
}
