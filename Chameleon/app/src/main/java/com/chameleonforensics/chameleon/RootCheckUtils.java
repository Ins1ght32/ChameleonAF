package com.chameleonforensics.chameleon;

import java.io.DataOutputStream;

public class RootCheckUtils {
    public static boolean hasRootAccess() {
        try {
            Process su = Runtime.getRuntime().exec("su");
            DataOutputStream os = new DataOutputStream(su.getOutputStream());
            os.writeBytes("exit\n");
            os.flush();
            int exitCode = su.waitFor();
            return (exitCode == 0);
        } catch (Exception e) {
            return false;
        }
    }
}
