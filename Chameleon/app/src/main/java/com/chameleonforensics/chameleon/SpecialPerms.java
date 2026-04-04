package com.chameleonforensics.chameleon;

import android.app.Activity;
import android.app.AppOpsManager;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.PowerManager;
import android.os.Process;
import android.provider.Settings;
import android.util.Log;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public final class SpecialPerms {
    private static final String TAG = "SpecialPerms";

    // Keep this aligned to what you consider "special" (AppOps / Settings toggles / confirmation flows)
    private static final Set<String> SPECIAL = new HashSet<>(Arrays.asList(
            "android.permission.MANAGE_EXTERNAL_STORAGE",
            "android.permission.SYSTEM_ALERT_WINDOW",
            "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS",
            "android.permission.PACKAGE_USAGE_STATS"
    ));

    private SpecialPerms() {}

    public static boolean isSpecialPerm(String perm) {
        return perm != null && SPECIAL.contains(perm);
    }

    public static boolean anyMissing(Context ctx, String[] perms) {
        if (ctx == null || perms == null || perms.length == 0) return false;
        for (String p : perms) {
            if (p == null) continue;
            if (!isGranted(ctx, p)) return true;
        }
        return false;
    }

    public static String firstMissing(Context ctx, String[] perms) {
        if (ctx == null || perms == null || perms.length == 0) return null;
        for (String p : perms) {
            if (p == null) continue;
            if (!isGranted(ctx, p)) return p;
        }
        return null;
    }

    public static boolean isGranted(Context ctx, String perm) {
        if (ctx == null || perm == null) return false;

        try {
            switch (perm) {
                case "android.permission.MANAGE_EXTERNAL_STORAGE":
                    // Android 11+ uses "All files access" gate
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        return android.os.Environment.isExternalStorageManager();
                    }
                    // Pre-R: not a real toggle; treat as "not applicable" (or true)
                    return true;

                case "android.permission.SYSTEM_ALERT_WINDOW":
                    // Overlay permission
                    return Settings.canDrawOverlays(ctx);

                case "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS":
                    // Battery optimization whitelist
                    PowerManager pm = (PowerManager) ctx.getSystemService(Context.POWER_SERVICE);
                    if (pm == null) return false;
                    return pm.isIgnoringBatteryOptimizations(ctx.getPackageName());

                case "android.permission.PACKAGE_USAGE_STATS":
                    // Usage access is AppOps-driven (GET_USAGE_STATS)
                    AppOpsManager aom = (AppOpsManager) ctx.getSystemService(Context.APP_OPS_SERVICE);
                    if (aom == null) return false;

                    // checkOpNoThrow expects the "uid" + package
                    int mode = aom.checkOpNoThrow(
                            AppOpsManager.OPSTR_GET_USAGE_STATS,
                            Process.myUid(),
                            ctx.getPackageName()
                    );

                    if (mode == AppOpsManager.MODE_ALLOWED) return true;

                    // MODE_DEFAULT typically means "not explicitly allowed" (treat as not granted)
                    return false;

                default:
                    // Unknown special perm -> treat as not granted so you notice it
                    Log.w(TAG, "Unknown special permission: " + perm);
                    return false;
            }
        } catch (Throwable t) {
            Log.e(TAG, "isGranted failed for " + perm, t);
            return false;
        }
    }

    public static boolean openSettingsFor(Activity a, String perm) {
        if (a == null || perm == null) return false;

        try {
            Intent i;

            switch (perm) {
                case "android.permission.MANAGE_EXTERNAL_STORAGE":
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        i = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                        i.setData(Uri.parse("package:" + a.getPackageName()));
                    } else {
                        // Fallback: app details
                        i = appDetailsIntent(a);
                    }
                    break;

                case "android.permission.SYSTEM_ALERT_WINDOW":
                    i = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION);
                    i.setData(Uri.parse("package:" + a.getPackageName()));
                    break;

                case "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS":
                    // This is a confirmation dialog flow
                    i = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
                    i.setData(Uri.parse("package:" + a.getPackageName()));
                    break;

                case "android.permission.PACKAGE_USAGE_STATS":
                    // No stable per-app deep link across OEMs; go to the list page
                    i = new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS);
                    break;

                default:
                    Log.w(TAG, "openSettingsFor: Unknown special permission: " + perm);
                    i = appDetailsIntent(a);
                    break;
            }

            // Safety: ensure it doesn't crash if called outside an activity context
            a.startActivity(i);
            return true;

        } catch (Throwable t) {
            Log.e(TAG, "Failed opening settings for " + perm, t);
            return false;
        }
    }

    private static Intent appDetailsIntent(Context ctx) {
        Intent i = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
        i.setData(Uri.parse("package:" + ctx.getPackageName()));
        return i;
    }

    public static void openFirstMissingSettings(Activity a, String[] perms) {
        if (perms == null) return;
        for (String p : perms) {
            if (isMissing(a, p)) {
                openSettingsFor(a, p);
                return;
            }
        }
    }

    public static boolean isMissing(Activity a, String perm) {
        if (perm == null) return false;
        String[] one = new String[]{perm};
        return anyMissing(a, one);
    }

}
