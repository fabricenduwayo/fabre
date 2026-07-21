package io.meterhub.legacy;

import io.meterhub.wire.Frame;
import java.util.ArrayList;
import java.util.List;

public final class LegacyReader {
    private LegacyReader() {}

    public static List<String> parse(String raw) {
        List<String> frames = new ArrayList<>();
        for (String part : raw.split(";")) {
            frames.add(Frame.encode(part));
        }
        return frames;
    }
}
