// app/src/main/java/com/chameleonforensics/chameleon/UiInjector.java
package com.chameleonforensics.chameleon;

import android.app.Activity;
import android.graphics.Typeface;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public class UiInjector {

    public static class RowRefs {
        public final String className;
        public final TextView statusView;
        RowRefs(String className, TextView statusView) {
            this.className = className;
            this.statusView = statusView;
        }
    }

    public static RowRefs[] attach(Activity a) {
        View root = a.findViewById(R.id.root_linear);
        LinearLayout col;
        if (root instanceof LinearLayout) {
            col = (LinearLayout) root;
        } else {
            ScrollView sc = new ScrollView(a);
            col = new LinearLayout(a);
            col.setOrientation(LinearLayout.VERTICAL);
            sc.addView(col);
            a.setContentView(sc);
        }

        // Title
        TextView title = new TextView(a);
        title.setText("Chameleon — Feature Autorun Status");
        title.setTextSize(18f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        col.addView(title);

        String[] classes = FeatureRegistry.featureClasses;
        String[] labels  = FeatureRegistry.featureLabels;
        if (classes == null) classes = new String[0];
        if (labels == null)  labels  = new String[0];

        RowRefs[] rows = new RowRefs[classes.length];

        for (int i = 0; i < classes.length; i++) {
            final String cls = classes[i];
            String label = (i < labels.length && labels[i] != null && !labels[i].isEmpty())
                    ? labels[i] : cls;

            LinearLayout row = new LinearLayout(a);
            row.setOrientation(LinearLayout.HORIZONTAL);

            TextView left = new TextView(a);
            left.setText("• " + label + " ");
            left.setTypeface(Typeface.MONOSPACE);
            left.setTextSize(14f);

            TextView status = new TextView(a);
            status.setText("Pending");
            status.setTypeface(Typeface.MONOSPACE);
            status.setTextSize(14f);

            row.addView(left);
            row.addView(status);
            col.addView(row);

            rows[i] = new RowRefs(cls, status);
        }
        return rows;
    }
}
