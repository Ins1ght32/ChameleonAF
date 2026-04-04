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
 * HoneyTokens – deploy honeytoken files and monitor them
 */
public class HoneyTokens {
    private static final String TAG = "HoneyTokens";

    // Keep global state
    private static final List<String> deployedFiles = new ArrayList<>();
    private static volatile boolean monitoringActive = false;

    /**
     * Entry point expected by feature framework
     */
	 
    public static boolean run(Activity activity) {
		Log.i(TAG, "Root Status Granted – starting Honey Token Deployment and Monitoring");
        startMonitoring(activity != null ? activity.getApplicationContext() : getAppContext());
        return true;
    }

	private static void writeHoneyWithSu(String path, String content) {
		try {
			// Ensure the parent directory exists
			String mkdirCmd = "mkdir -p \"" + new File(path).getParent() + "\"";
			Runtime.getRuntime().exec(new String[]{"su", "-c", mkdirCmd}).waitFor();

			// Write content
			String cmd = "echo \"" + content.replace("\"", "\\\"") + "\" > \"" + path + "\"";
			Process p = Runtime.getRuntime().exec(new String[]{"su", "-c", cmd});
			int exitCode = p.waitFor();

			if (exitCode == 0) {
				Log.i("HoneyTokens", "Honey token written: " + path);
			} else {
				Log.e("HoneyTokens", "Failed to write honey token at " + path + " (exit=" + exitCode + ")");
			}
		} catch (Exception e) {
			Log.e("HoneyTokens", "Error writing honey token", e);
		}
	}

    /**
	 * Deploy honeytoken files into the four fixed directories
	 */
	private static void deployHoneytokens(Context ctx) {
		try {
			String ts = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
			String filename = "honeytoken_" + ts + ".txt";
			String content = "HoneyToken generated at " + ts;

			String[] baseDirs = {
				"/storage/emulated/0",
				//"/storage/emulated/0/Documents",
				//"/storage/emulated/0/Pictures",
				//"/storage/emulated/0/Downloads"
			};

			for (String dir : baseDirs) {
				String fullPath = dir + "/" + filename;
				writeHoneyWithSu(fullPath, content);
				deployedFiles.add(fullPath);
			}

		} catch (Exception e) {
			Log.e(TAG, "Failed to deploy honeytokens", e);
		}
	}

    /**
     * Start monitoring honeytoken files with inotify via su
     */
    private static void startMonitoring(final Context ctx) {
        deployHoneytokens(ctx);
        monitoringActive = true;

        Thread t = new Thread(() -> {

            while (monitoringActive) {
                try {
                    for (String path : deployedFiles) {
                        String cmd = "su -c inotifyd - " + path;
						Process proc = Runtime.getRuntime().exec(cmd);
                        BufferedReader br = new BufferedReader(new InputStreamReader(proc.getInputStream()));
                        String line;
                        while ((line = br.readLine()) != null) {
							String logMessage = "Honeytoken access detected: " + line;
                            Log.w(TAG, logMessage);
                            recordTriggerCompat(ctx, TAG, logMessage);
                        }
                        proc.waitFor();
                    }
                    // Sleep between rechecks
                    Thread.sleep(10000);
                } catch (Exception e) {
                    Log.e(TAG, "Monitoring error", e);
                }
            }
        });
        t.setDaemon(true);
        t.start();
    }

    /**
     * Stop monitoring
     */
    public static void stopMonitoring() {
        monitoringActive = false;
    }

    /**
     * Utility: run su command
     */
    private static void runSuCommand(String cmd) throws Exception {
        Process proc = Runtime.getRuntime().exec(cmd);
        proc.waitFor();
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
