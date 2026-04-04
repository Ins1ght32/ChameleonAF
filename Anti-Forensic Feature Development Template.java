package com.chameleonforensics.chameleon;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.Application;
import android.content.Context;
import android.util.Log;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;

/*
 * =========================================================================
 * FEATURE TEMPLATE
 * =========================================================================
 * 
 * The following are to be replaced if they exist in the code:
 * Class Name    : __CLASS_NAME__
 * Description   : __FEATURE_DESCRIPTION__
 *
 * Notes:
 * - Only edit the following areas:
 *   1) Imports (add feature-specific imports)
 *   2) RUN BODY in run()
 *   3) Feature-specific helper methods (if any)
 *	 4) Where the position of recordTriggerCompat(ctx, TAG) / 
 *		recordTriggerCompat(ctx, TAG, "Custom Message") is called in run() 
 *		or in your Feature-specific helper methods
 * 
 */
public final class __CLASS_NAME__ {

    private static final String TAG = "__CLASS_NAME__";

    // =========================================================================
    // ENTRYPOINT (To keep consistent across all features)
    // =========================================================================
    public static boolean run(Activity activity) {
        Context ctx = (activity != null) ? activity.getApplicationContext() : getAppContext();
        if (ctx == null) {
            Log.e(TAG, "App context unavailable; feature not started");
            return;
        }

        try {
            Log.i(TAG, "Starting feature: " + TAG);

            // --------------------------------------------------------------------
            // RUN BODY (THIS IS WHAT YOU EDIT PER YOUR ANTI-FORESNIC LOGIC)
            // --------------------------------------------------------------------
            // Examples of what goes here:
            // - Logic for monitoring screenshots ran by ADB cmd
            // - Logic for deploying and monitoring honey tokens
            //
            // __RUN_BODY__

            // --------------------------------------------------------------------
            // REPORTING TRIGGER (consistent)
			// --------------------------------------------------------------------
			// The following code is to be called when your anti-forensic logic has
			// reached a point of triggering. The code is to facilitate reporting 
			// on the controller application. An alternative code is provided in
			// subsequent commented line.
			
			recordTriggerCompat(ctx, TAG);
            //recordTriggerCompat(ctx, TAG, "Custom Message")
			
			
			// --------------------------------------------------------------------

            Log.i(TAG, "Feature completed: " + TAG);

        } catch (Throwable t) {
            Log.e(TAG, "Feature execution failed", t);
        }
		
        return true;
    }

	// ====== Feature-specific Helpers ====================================
	
	// (YOU CAN UTILISE THIS SPACE FOR ANY CUSTOM FUNCTIONS UTILISED IN RUN)

	// Execute a root shell command
	private static void runSuCommand(String cmd) throws Exception {
        Process proc = Runtime.getRuntime().exec(cmd);
        proc.waitFor();
    }
	
	// Execute a non-root shell command
	private static Process runShCommand(String cmd) throws IOException {
		return Runtime.getRuntime().exec(new String[]{"sh", "-c", cmd});
	}
	
	// Read stdout fully from a running process
	private static String readStdout(Process p) throws Exception {
		BufferedReader br = new BufferedReader(
				new InputStreamReader(p.getInputStream())
		);

		StringBuilder sb = new StringBuilder();
		String line;
		while ((line = br.readLine()) != null) {
			sb.append(line).append('\n');
		}
		return sb.toString();
	}

    // ====== Required Helpers (DO NOT DELETE OR MODIFY) ===================

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
