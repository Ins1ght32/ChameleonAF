package com.chameleonforensics.chameleon;

import android.content.Context;
import android.os.Build;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Reads the NDJSON line-by-line and produces a compact summary JSON:
 * {
 *   "schema":"chameleon.report.v1",
 *   "device":{"sdk":34,...},
 *   "session_id":"20250904-223000",
 *   "events":[ ... raw lines ... ],
 *   "features":{
 *       "AntiAgent":{"count":3,"first_ts":"...","last_ts":"..."}
 *   }
 * }
 */

public final class ReportFinaliser {
    private static final String TAG = "ReportFinalizer";

    private ReportFinaliser() {}

    public static File finalizeNow(Context ctx) {
        ctx = ctx.getApplicationContext();
        File src = ReportCore.getNdjsonFile(ctx);
        File dst = ReportCore.getFinalJsonFile(ctx);

        JSONArray events = new JSONArray();
        Map<String, FeatureAgg> agg = new LinkedHashMap<>();

        try (BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(src), StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) {
                try {
                    JSONObject e = new JSONObject(line);
                    events.put(e);
                    String f = e.optString("feature", "unknown");
                    String ts = e.optString("ts", "");
                    FeatureAgg a = agg.get(f);
                    if (a == null) { a = new FeatureAgg(); agg.put(f, a); }
                    a.count++;
                    if (a.firstTs == null || ts.compareTo(a.firstTs) < 0) a.firstTs = ts;
                    if (a.lastTs == null  || ts.compareTo(a.lastTs)  > 0) a.lastTs  = ts;
                } catch (Throwable ignoreSingleBadLine) {}
            }
        } catch (FileNotFoundException e) {
            // If NDJSON doesn’t exist yet, still produce an empty summary
        } catch (Exception e) {
            Log.e(TAG, "read ndjson failed", e);
        }

        JSONObject root = new JSONObject();
        try {
            root.put("schema", "chameleon.report.v1");
            root.put("session_id", src.getName().replace(".ndjson", "").replace("session-", ""));
            root.put("device", new JSONObject()
                    .put("sdk", Build.VERSION.SDK_INT));
            root.put("events", events);

            JSONObject features = new JSONObject();
            for (Map.Entry<String, FeatureAgg> e : agg.entrySet()) {
                features.put(e.getKey(), new JSONObject()
                        .put("count", e.getValue().count)
                        .put("first_ts", e.getValue().firstTs)
                        .put("last_ts", e.getValue().lastTs));
            }
            root.put("features", features);

            try (FileOutputStream fos = new FileOutputStream(dst)) {
                fos.write(root.toString(2).getBytes(StandardCharsets.UTF_8));
            }
        } catch (Exception e) {
            Log.e(TAG, "write final json failed", e);
        }
        return dst;
    }

    private static final class FeatureAgg {
        int count = 0;
        String firstTs = null;
        String lastTs  = null;
    }
}
