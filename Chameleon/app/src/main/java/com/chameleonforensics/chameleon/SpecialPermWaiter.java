package com.chameleonforensics.chameleon;

import android.app.Activity;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

final class SpecialPermWaiter {
    private static final String TAG = "SpecialPermWaiter";

    private static final class Pending {
        final UiInjector.RowRefs row;
        final String[] perms;
        boolean settingsOpened;
        long lastOpenMs;

        Pending(UiInjector.RowRefs r, String[] p) {
            row = r;
            perms = p;
        }
    }

    private static final Map<String, Long> permLastOpenMs = new HashMap<>();

    private static final List<Pending> queued = new ArrayList<>();
    private static boolean loopStarted = false;

    // Global throttle: don’t open settings more often than this per feature
    private static final long OPEN_COOLDOWN_MS = 4000;

    // Optional: if you want "reopen once after user returns", track resume edges
    private static boolean appInForeground = true;

    public static void register(UiInjector.RowRefs row, String[] perms) {
        if (row == null || perms == null || perms.length == 0) return;

        // dedup by className
        for (Pending p : queued) {
            if (p.row != null && p.row.className != null && p.row.className.equals(row.className)) {
                return;
            }
        }
        queued.add(new Pending(row, perms));
    }

    public static void startLoop(Activity a) {
        if (loopStarted) return;
        loopStarted = true;

        Handler h = new Handler(Looper.getMainLooper());
        final Runnable[] checker = new Runnable[1];

        checker[0] = () -> {
            try {
                if (queued.isEmpty()) return;

                long now = SystemClock.elapsedRealtime();

                // iterate on a copy so we can remove safely
                List<Pending> copy = new ArrayList<>(queued);

                for (Pending p : copy) {
                    if (p.row == null) continue;

                    // If perms now granted -> run feature and remove
                    if (!SpecialPerms.anyMissing(a, p.perms)) {
                        Log.i(TAG, "Special perms granted for " + p.row.className + ", running…");
                        AutoRunner.runFeatureWithGates(a, p.row);
                        queued.remove(p);
                        continue;
                    }

                    // Still missing -> open settings (throttled PER PERMISSION, shared across all features)
                    if (appInForeground) {
                        String missing = SpecialPerms.firstMissing(a, p.perms);
                        if (missing != null) {
                            long last = permLastOpenMs.containsKey(missing)
                                    ? permLastOpenMs.get(missing)
                                    : 0L;

                            if (last == 0L || (now - last) > OPEN_COOLDOWN_MS) {
                                Log.i(TAG,
                                        "Opening settings for perm=" + missing +
                                                " (triggered by " + p.row.className + ")");

                                SpecialPerms.openSettingsFor(a, missing);

                                permLastOpenMs.put(missing, now);

                                // optional bookkeeping
                                p.settingsOpened = true;
                                p.lastOpenMs = now;
                            }
                        }
                    }

                }

            } catch (Throwable t) {
                Log.e(TAG, "checker loop error", t);
            } finally {
                // Keep polling until queue is empty
                if (!queued.isEmpty()) {
                    h.postDelayed(checker[0], 1500);
                } else {
                    // reset for next batch
                    loopStarted = false;
                }
            }
        };

        h.post(checker[0]);
    }

    /** Call from MainActivity.onResume() */
    public static void onAppForeground() {
        appInForeground = true;
        // Don’t auto-open here; the loop will decide based on cooldown & missing perms.
    }

    /** Call from MainActivity.onPause() */
    public static void onAppBackground() {
        appInForeground = false;
    }

    private SpecialPermWaiter() {}
}
