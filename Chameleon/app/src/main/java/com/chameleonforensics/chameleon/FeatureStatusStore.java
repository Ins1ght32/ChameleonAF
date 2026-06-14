package com.chameleonforensics.chameleon;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public final class FeatureStatusStore {

    private static final Map<String, FeatureState> states = new HashMap<>();

    private FeatureStatusStore() {}

    public static synchronized void initFeature(String featureName) {
        if (!states.containsKey(featureName)) {
            states.put(featureName, new FeatureState(featureName));
        }
    }

    public static synchronized void setStatus(String featureName, String status) {
        initFeature(featureName);
        states.get(featureName).status = status;
    }

    public static synchronized void markTriggered(String featureName, String timestamp) {
        initFeature(featureName);
        FeatureState s = states.get(featureName);
        s.triggerCount++;
        s.latestTriggerTime = timestamp;
    }

    public static synchronized Map<String, FeatureState> snapshot() {
        return Collections.unmodifiableMap(new HashMap<>(states));
    }

    public static synchronized Summary getSummary() {
        int total = states.size();
        int active = 0;
        int waitingRoot = 0;
        int waitingPermissions = 0;
        int pending = 0;
        int failed = 0;
        int totalTriggers = 0;

        for (FeatureState s : states.values()) {
            String status = s.status == null ? "" : s.status;

            if ("OK".equalsIgnoreCase(status)) {
                active++;
            } else if (status.toLowerCase().contains("waiting for root")) {
                waitingRoot++;
            } else if (status.toLowerCase().contains("waiting for permissions")) {
                waitingPermissions++;
            } else if (status.toLowerCase().contains("pending")
                    || status.toLowerCase().contains("running")) {
                pending++;
            } else if (status.toLowerCase().contains("error")
                    || status.toLowerCase().contains("timeout")
                    || status.toLowerCase().contains("failed")) {
                failed++;
            }

            totalTriggers += s.triggerCount;
        }

        return new Summary(total, active, waitingRoot, waitingPermissions, pending, failed, totalTriggers);
    }

    public static final class FeatureState {
        public final String featureName;
        public String status = "Pending";
        public int triggerCount = 0;
        public String latestTriggerTime = null;

        private FeatureState(String featureName) {
            this.featureName = featureName;
        }
    }

    public static final class Summary {
        public final int total;
        public final int active;
        public final int waitingRoot;
        public final int waitingPermissions;
        public final int pending;
        public final int failed;
        public final int totalTriggers;

        private Summary(int total, int active, int waitingRoot, int waitingPermissions, int pending, int failed, int totalTriggers) {
            this.total = total;
            this.active = active;
            this.waitingRoot = waitingRoot;
            this.waitingPermissions = waitingPermissions;
            this.pending = pending;
            this.failed = failed;
            this.totalTriggers = totalTriggers;
        }
    }
}