package com.chameleonforensics.chameleon;

import android.util.Log;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;

public class RootCheckUtils {
    private static final String TAG = "RootCheckUtils";

    public static boolean hasRootAccess() {
        Process su = null;

        try {
            su = Runtime.getRuntime().exec("su");

            DataOutputStream os = new DataOutputStream(su.getOutputStream());
            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(su.getInputStream())
            );

            os.writeBytes("id\n");
            os.writeBytes("exit\n");
            os.flush();

            String line;
            boolean gotRoot = false;

            while ((line = reader.readLine()) != null) {
                Log.d(TAG, "su output: " + line);

                if (line.contains("uid=0")) {
                    gotRoot = true;
                    break;
                }
            }

            int exitCode = su.waitFor();
            return gotRoot && exitCode == 0;

        } catch (Exception e) {
            Log.e(TAG, "Root check failed", e);
            return false;

        } finally {
            if (su != null) {
                su.destroy();
            }
        }
    }
}