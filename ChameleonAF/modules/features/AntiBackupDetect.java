package com.chameleonforensics.chameleon;

import android.app.Activity;
import android.content.Context;
import android.os.Handler;
import android.util.Log;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import android.annotation.SuppressLint;
import android.app.Application;

public class AntiBackupDetect {

    private static final String TAG = "AntiBackupDetect";
    private static final int CHECK_INTERVAL_MS = 5000; // 5 seconds

    public static boolean run(Activity activity) {
		try {
			Log.i(TAG, "Root Status Granted – starting su+ps monitor");
			startMonitoring(activity.getApplicationContext());
			return true;
		}catch (Exception e){
			 Log.e(TAG, "Error during run", e);
			return false;
		}
    }

    public static void startMonitoring(final Context context) {
        Log.e(TAG, "ADB backup su+ps monitor started");

        final Handler handler = new Handler();
        final Runnable[] checker = new Runnable[1];  // workaround to reference from inside itself

        checker[0] = new Runnable() {
            @Override
            public void run() {
                if (isAdbBackupRunningViaPs()) {
                    Log.e(TAG, "ADB Backup detected via `su` + ps! Stopping monitor.");
					recordTriggerCompat(context, TAG);
                    handler.removeCallbacks(checker[0]);  // stop further checks
                } else {
                    handler.postDelayed(this, CHECK_INTERVAL_MS);
                }
            }
        };

        handler.post(checker[0]);
    }

    private static boolean isAdbBackupRunningViaPs() {
        try {
            Process process = Runtime.getRuntime().exec(new String[]{"su", "-c", "ps"});
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.contains("backup") || line.contains("BackupManager") || line.contains("backupconfirm")) {
                    Log.e(TAG, "Detected process line: " + line);
                    return true;
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Error running ps via su", e);
        }
        return false;
    }
	
	// ====== Required helpers ======
	
	@SuppressLint("PrivateApi")
    private static Context getAppContext() {
        try {
            Class<?> at = Class.forName("android.app.ActivityThread");
            Object app = at.getMethod("currentApplication").invoke(null);
            if (app instanceof Application) {
                return ((Application) app).getApplicationContext();
            }
        } catch (Throwable ignored) {}
        return null;
    }
	

	private static void recordTriggerCompat(Context ctx, String tag) {
		if (ctx == null) ctx = getAppContext();
		if (ctx == null) {
			android.util.Log.w(TAG, "recordTriggerCompat: no Context; skipping");
			return;
		}
		try {
			tag = "com.chameleonforensics.chameleon" + "." + tag;
			// Build FQCN dynamically so it works after smali injection
			String fqcn = ctx.getPackageName() + ".ReportCore";

			Class<?> rc = Class.forName(fqcn);
			java.lang.reflect.Method m = rc.getMethod(
					"recordTrigger",
					android.content.Context.class,
					java.lang.String.class
			);
			m.invoke(null, ctx.getApplicationContext(), tag);
			android.util.Log.i(TAG, "recordTriggerCompat: invoked " + fqcn + ".recordTrigger for " + tag);
		} catch (Throwable t) {
			android.util.Log.w(TAG, "recordTriggerCompat: ReportCore not present/failed; skipping", t);
		}
	}
	
	private static void recordTriggerCompat(Context ctx, String tag, String custom) {
		if (ctx == null) ctx = getAppContext();
		if (ctx == null) {
			android.util.Log.w(TAG, "recordTriggerCompat: no Context; skipping");
			return;
		}
		try {
			tag = "com.chameleonforensics.chameleon" + "." + tag;
			// Build FQCN dynamically so it works after smali injection
			String fqcn = ctx.getPackageName() + ".ReportCore";

			Class<?> rc = Class.forName(fqcn);
			java.lang.reflect.Method m = rc.getMethod(
					"recordTrigger",
					android.content.Context.class,
					java.lang.String.class,
					java.lang.String.class
			);
			m.invoke(null, ctx.getApplicationContext(), tag, custom);
			android.util.Log.i(TAG, "recordTriggerCompat: invoked " + fqcn + ".recordTrigger for " + tag);
		} catch (Throwable t) {
			android.util.Log.w(TAG, "recordTriggerCompat: ReportCore not present/failed; skipping", t);
		}
	}
}
