package com.chameleonforensics.chameleon;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.Application;
import android.content.Context;
import android.os.Environment;
import android.util.Log;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * ADBScreenCapture Detection – Detect for screencap command ran
 */
public class ADBScreenCapture {
    private static final String TAG = "ADBScreenCapture";

    // Keep global state
    private static Thread monitorThread;
    private static volatile boolean running = true;

    /**
     * Entry point expected by feature framework
     */
	 
    public static boolean run(Activity activity) {
		Log.i(TAG, "Root Status Granted – starting ADB Screen Capture Monitoring");
        startMonitoring(activity != null ? activity.getApplicationContext() : getAppContext());
        return true;
    }

	private static void startMonitoring(final Context ctx) {
        monitorThread = new Thread(() -> {
            String lastPid = "";
            while (running) {
                try {
                    // Use helper to run ps via su
                    Process p = runSuCommand("ps -A | grep -w screencap");

                    BufferedReader reader = new BufferedReader(
                            new InputStreamReader(p.getInputStream())
                    );
                    String line;
                    while ((line = reader.readLine()) != null) {
                        line = line.trim();
                        if (!line.isEmpty()) {
                            String[] parts = line.split("\\s+");
                            if (parts.length > 2) {
                                String user = parts[0];   // usually first col
                                String pid = parts[1];    // usually second col

                                if ("shell".equals(user) && !pid.equals(lastPid)) {
                                    Log.e(TAG, "ADB screencap detected! PID=" + pid + " User=" + user);
                                    recordTriggerCompat(ctx, TAG);
                                    lastPid = pid;
                                }
                            }
                        }
                    }
                    reader.close();
                    p.waitFor();
                    Thread.sleep(200); // polling interval
                } catch (Exception e) {
                    Log.e(TAG, "Error in monitor loop", e);
                }
            }
        });
        monitorThread.start();
    }

    /**
     * Utility: run su command
     */
    private static Process runSuCommand(String cmd) throws Exception {
        return Runtime.getRuntime().exec(new String[]{"su", "-c", cmd});
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
