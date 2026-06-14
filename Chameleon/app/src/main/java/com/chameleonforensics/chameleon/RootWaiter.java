package com.chameleonforensics.chameleon;

import android.app.Activity;
import android.os.Handler;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

public class RootWaiter {
    private static final String TAG = "RootWaiter";

    private static final List<UiInjector.RowRefs> queued = new ArrayList<>();
    private static boolean loopStarted = false;
    private static boolean rootGranted = false;

    public static synchronized boolean isRootGranted() {
        return rootGranted;
    }

    public static synchronized void registerRootFeature(UiInjector.RowRefs row) {
        if (row == null || row.className == null) return;

        for (UiInjector.RowRefs existing : queued) {
            if (existing != null
                    && existing.className != null
                    && existing.className.equals(row.className)) {
                return;
            }
        }

        queued.add(row);
    }

    public static void startLoop(Activity a) {
        if (a == null) return;

        synchronized (RootWaiter.class) {
            if (rootGranted) {
                runQueuedOnUi(a);
                return;
            }

            if (loopStarted) return;
            loopStarted = true;
        }

        Handler h = new Handler(a.getMainLooper());
        final Runnable[] checker = new Runnable[1];

        checker[0] = () -> {
            new Thread(() -> {
                boolean granted = RootCheckUtils.hasRootAccess();

                a.runOnUiThread(() -> {
                    if (granted) {
                        Log.i(TAG, "Root granted! Executing delayed features…");

                        synchronized (RootWaiter.class) {
                            rootGranted = true;
                            loopStarted = false;
                        }

                        runQueuedOnUi(a);

                    } else {
                        Log.d(TAG, "Root not yet granted… retrying");
                        h.postDelayed(checker[0], 4000);
                    }
                });
            }).start();
        };

        h.post(checker[0]);
    }

    private static void runQueuedOnUi(Activity a) {
        List<UiInjector.RowRefs> copy;

        synchronized (RootWaiter.class) {
            copy = new ArrayList<>(queued);
            queued.clear();
        }

        for (UiInjector.RowRefs r : copy) {
            /*
             * Use gated runner, not direct runner.
             * This prevents a root+special-perm feature from skipping
             * its special permission gate if it somehow entered the root queue.
             */
            AutoRunner.runFeatureWithGates(a, r);
        }
    }
}