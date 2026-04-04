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

    public static void registerRootFeature(UiInjector.RowRefs row) {
        queued.add(row);
    }

    public static void startLoop(Activity a) {
        if (loopStarted) return;
        loopStarted = true;

        Handler h = new Handler(a.getMainLooper());
        final Runnable[] checker = new Runnable[1];
        checker[0] = () -> {
            if (RootCheckUtils.hasRootAccess()) {
                Log.i(TAG, "Root granted! Executing delayed features…");

                for (UiInjector.RowRefs r : queued) {
                    AutoRunner.runFeatureImmediately(a, r);
                }
                queued.clear();
            } else {
                Log.d(TAG, "Root not yet granted… retrying");
                h.postDelayed(checker[0], 2000); // 2s retry
            }
        };

        h.post(checker[0]);
    }
}
