package com.chameleonforensics.chameleon;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import java.io.File;

public class ReportReceiver extends BroadcastReceiver {
    private static final String TAG = "ReportReceiver";

    public static final String ACTION_FINALIZE_REPORT =
            "com.chameleonforensics.chameleon.ACTION_FINALIZE_REPORT";
    public static final String EXTRA_REPORT_PATH = "report_path";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null) return;
        String action = intent.getAction();
        if (ACTION_FINALIZE_REPORT.equals(action)) {
            File out = ReportFinaliser.finalizeNow(context);
            Log.i(TAG, "Final report at: " + (out != null ? out.getAbsolutePath() : "null"));
            // Optionally rebroadcast path to your desktop controller (or leave it as ADB-pull)
            // You can also add: context.sendBroadcast(new Intent(...).putExtra(EXTRA_REPORT_PATH, out.getAbsolutePath()));
        }
    }
}
