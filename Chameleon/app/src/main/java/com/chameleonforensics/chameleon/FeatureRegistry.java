// app/src/main/java/com/chameleonforensics/chameleon/FeatureRegistry.java
package com.chameleonforensics.chameleon;

public final class FeatureRegistry {
    // The build engine will generate these as smali arrays at build-time.
    public static String[] featureClasses = new String[0]; // e.g., "com.foo.AntiAgent"
    public static String[] featureLabels  = new String[0]; // e.g., "Anti-Agent"
    private FeatureRegistry() {}
}
