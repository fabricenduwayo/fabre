package io.meterhub.app;

import io.meterhub.legacy.LegacyReader;

public final class LegacyImport {
    private LegacyImport() {}

    public static int importLegacy(String raw) {
        return LegacyReader.parse(raw).size();
    }
}
