package com.chameleonforensics.chameleon;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.Application;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.Uri;
import android.os.Build;
import android.util.Log;

public final class AntiAgent {
    private static final String TAG = "AntiAgent";

    // compiler.py can overwrite this value.
    private static final String TARGET_PACKAGE = "com.example.helloworld";

    private static BroadcastReceiver sReceiver;
    private static boolean sRegistered;

    private AntiAgent() { /* no instances */ }

    /**
     * EXACT signature the controller expects:
     * .method public static run(Landroid/app/Activity;)V
     */
	 
    public static boolean run(Activity activity) {
		try {
			Log.i(TAG, "AntiAgent.run() — starting watcher for: " + TARGET_PACKAGE);
			run(activity.getApplicationContext());
			return true;
		}catch (Exception e){
			Log.e(TAG, "Error during run", e);
			return false;
		}
    }

    /** Optional zero-arg entrypoint */
    public static void run() {
        Context ctx = getAppContext();
        if (ctx == null) {
            Log.e(TAG, "App context unavailable; watcher not started");
            return;
        }
        Log.i(TAG, "AntiAgent.run() — starting (no-arg)");
        run(ctx);
    }

    /** Core: register the package-added/updated watcher */
    public static synchronized void run(Context context) {
        if (sRegistered) {
            Log.i(TAG, "Watcher already registered");
            return;
        }
        try {
            IntentFilter filter = new IntentFilter();
            filter.addAction(Intent.ACTION_PACKAGE_ADDED);
            filter.addAction(Intent.ACTION_PACKAGE_REPLACED);
            filter.addDataScheme("package");

            sReceiver = new PkgReceiver();

            if (Build.VERSION.SDK_INT >= 33) {
                // Reflection so it still compiles under --release 8
                try {
                    Context.class
                            .getMethod("registerReceiver",
                                    BroadcastReceiver.class,
                                    IntentFilter.class,
                                    int.class)
                            .invoke(context.getApplicationContext(),
                                    sReceiver,
                                    filter,
                                    2 /* RECEIVER_EXPORTED */);
                } catch (Throwable t) {
                    Log.e(TAG, "Reflection registerReceiver failed", t);
                }
            } else {
                context.getApplicationContext().registerReceiver(sReceiver, filter);
            }

            sRegistered = true;
            Log.e(TAG, "Package watcher registered for target=" + TARGET_PACKAGE +
                    " (SDK=" + Build.VERSION.SDK_INT + ")");
        } catch (Throwable t) {
            Log.e(TAG, "Failed to register package watcher", t);
        }
    }

    /** Named static inner class (predictable file: AntiAgent$PkgReceiver.smali) */
    public static final class PkgReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context c, Intent intent) {
            if (intent == null) return;
            final String action = intent.getAction();
            final Uri data = intent.getData();
            final String pkg = (data != null) ? data.getSchemeSpecificPart() : null;

            Log.e(TAG, "PACKAGE EVENT: action=" + action +
                    " pkg=" + pkg +
                    " target=" + TARGET_PACKAGE);

            if (Intent.ACTION_PACKAGE_ADDED.equals(action)
                    || Intent.ACTION_PACKAGE_REPLACED.equals(action)) {
                if (pkg != null && TARGET_PACKAGE.equals(pkg)) {
                    Log.e(TAG, "✔ Detected target package event: " + action + " for " + pkg);
                    // TODO: add your reaction here if needed
					recordTriggerCompat(c, TAG);
                }
            }
        }
    }

    /** Cleanly stop the watcher */
    public static synchronized void shutdown(Context context) {
        if (!sRegistered || sReceiver == null) return;
        try {
            context.getApplicationContext().unregisterReceiver(sReceiver);
            Log.i(TAG, "Package watcher unregistered");
        } catch (Throwable t) {
            Log.e(TAG, "Error unregistering receiver", t);
        } finally {
            sReceiver = null;
            sRegistered = false;
        }
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
