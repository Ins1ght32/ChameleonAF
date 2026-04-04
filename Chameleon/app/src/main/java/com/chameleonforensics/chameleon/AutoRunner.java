package com.chameleonforensics.chameleon;

import android.app.Activity;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.TextView;

public class AutoRunner {
    private static final String TAG = "AutoRunner";

    public static void runAllWithStagger(Activity a, UiInjector.RowRefs[] rows, long delayMs) {
        if (rows == null) return;

        Handler h = new Handler(Looper.getMainLooper());
        final boolean[] rootNeeded = {false};  // track if any feature requires root
        final boolean[] specialNeeded = {false};

        for (int i = 0; i < rows.length; i++) {
            final int idx = i;
            long when = i * Math.max(0L, delayMs);

            h.postDelayed(() -> {
                UiInjector.RowRefs r = rows[idx];
                setStatus(r.statusView, "Pending");

                try {
                    Class<?> c = Class.forName(r.className);

                    String[] special = SpecialFeatureRequirements.getSpecialPerms(r.className);
                    if (special != null && special.length > 0 && SpecialPerms.anyMissing(a, special)) {
                        setStatus(r.statusView, "Waiting for permissions…");
                        SpecialPermWaiter.register(r, special);
                        SpecialPermWaiter.startLoop(a);
                        return;
                    }


                    boolean needsRoot = false;

                    try {
                        needsRoot = (boolean) c.getMethod("requiresRoot").invoke(null);
                    } catch (NoSuchMethodException nsme) {
                        Log.w(TAG, "No requiresRoot() for " + r.className + " — assuming false");
                    }

                    if (needsRoot) {
                        rootNeeded[0] = true; // flag that root is needed by at least one feature
                        setStatus(r.statusView, "Waiting for root…");
                        RootWaiter.registerRootFeature(r);
                    } else {
                        runFeatureImmediately(a, r);
                    }

                } catch (Throwable t) {
                    ReportCore.recordTriggerState(a, r.className, "initialise_failed", "Reflection error");
                    setStatus(r.statusView, "Error: reflection");
                    Log.e(TAG, "Failed preparing feature: " + r.className, t);
                }
            }, when);
        }

        // Delay root loop start slightly to give time for features to be registered
        h.postDelayed(() -> {
            if (specialNeeded[0]) {
                SpecialPermWaiter.startLoop(a);
            } else {
                Log.i(TAG, "No features require special perms. Skipping SpecialPermWaiter.");
            }

            if (rootNeeded[0]) {
                RootWaiter.startLoop(a);
            } else {
                Log.i(TAG, "No features require root. Skipping RootWaiter.");
            }
        }, rows.length * delayMs + 100); // ensure it's called after all h.postDelayed calls above
    }

    public static void runFeatureImmediately(Activity a, UiInjector.RowRefs r) {
        setStatus(r.statusView, "Running…");
        try {
            Class<?> c = Class.forName(r.className);
            boolean result = (boolean) c.getMethod("run", Activity.class).invoke(null, a);
            if (result) {
                ReportCore.recordTriggerState(a, r.className, "initialisation_completed");
                setStatus(r.statusView, "OK");
            } else {
                ReportCore.recordTriggerState(a, r.className, "initialise_failed", "Returned false");
                setStatus(r.statusView, "Error: failed");
            }
        } catch (Throwable t) {
            ReportCore.recordTriggerState(a, r.className, "initialise_failed", t.getClass().getSimpleName());
            setStatus(r.statusView, "Error: " + t.getClass().getSimpleName());
            Log.e(TAG, "Feature run failed: " + r.className, t);
        }
    }

    private static void setStatus(final TextView tv, final String text) {
        if (tv == null) return;
        Runnable r = () -> {
            tv.setText(text);
            switch (text) {
                case "Pending":
                    tv.setTextColor(0xFF888888); // gray
                    break;
                case "Running…":
                    tv.setTextColor(0xFFE6B800); // amber/yellow
                    break;
                case "OK":
                    tv.setTextColor(0xFF2E7D32); // green
                    break;
                case "Waiting for root…":
                    tv.setTextColor(0xFF888888); // gray
                    break;
                case "Timeout":
                    tv.setTextColor(0xFFFF4444); // red
                    break;
                case "Waiting for permissions…":
                    tv.setTextColor(0xFF888888); // gray (or pick a different one)
                    break;
                default:
                    tv.setTextColor(0xFFB71C1C); // red for errors
                    break;
            }
        };
        if (Looper.myLooper() == Looper.getMainLooper()) {
            r.run();
        } else {
            new Handler(Looper.getMainLooper()).post(r);
        }
    }

    public static void runFeatureWithGates(Activity a, UiInjector.RowRefs r) {
        if (a == null || r == null) return;

        try {
            // Special perms gate (defensive; should already be satisfied when called from waiter)
            String[] special = SpecialFeatureRequirements.getSpecialPerms(r.className);
            if (special != null && special.length > 0 && SpecialPerms.anyMissing(a, special)) {
                setStatus(r.statusView, "Waiting for permissions…");
                SpecialPermWaiter.register(r, special);
                SpecialPermWaiter.startLoop(a);
                return;
            }

            // Root gate
            Class<?> c = Class.forName(r.className);
            boolean needsRoot = false;
            try {
                needsRoot = (boolean) c.getMethod("requiresRoot").invoke(null);
            } catch (NoSuchMethodException nsme) {
                Log.w(TAG, "No requiresRoot() for " + r.className + " — assuming false");
            }

            if (needsRoot) {
                setStatus(r.statusView, "Waiting for root…");
                RootWaiter.registerRootFeature(r);
                RootWaiter.startLoop(a);
                return;
            }

            // No gates -> run
            runFeatureImmediately(a, r);

        } catch (Throwable t) {
            ReportCore.recordTriggerState(a, r.className, "initialise_failed", t.getClass().getSimpleName());
            setStatus(r.statusView, "Error: " + t.getClass().getSimpleName());
            Log.e(TAG, "runFeatureWithGates failed: " + r.className, t);
        }
    }

}
