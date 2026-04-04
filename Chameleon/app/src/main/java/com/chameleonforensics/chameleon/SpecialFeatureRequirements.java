package com.chameleonforensics.chameleon;

public class SpecialFeatureRequirements {
    // Patched by Python during build
    // Each row: { "com.feature.ClassName", "perm1", "perm2", ... }
    public static String[][] SPECIAL_PERMS_BY_FEATURE = new String[][]{
            // default empty; patched
            // {"com.chameleonforensics.features.X", "android.permission.MANAGE_EXTERNAL_STORAGE"}
    };

    public static String[] getSpecialPerms(String className) {
        if (SPECIAL_PERMS_BY_FEATURE == null) return null;
        for (String[] row : SPECIAL_PERMS_BY_FEATURE) {
            if (row != null && row.length > 0 && className.equals(row[0])) {
                if (row.length == 1) return new String[0];
                String[] perms = new String[row.length - 1];
                System.arraycopy(row, 1, perms, 0, perms.length);
                return perms;
            }
        }
        return null; // null = "no mapping"
    }
}
