// app/src/main/java/com/chameleonforensics/chameleon/UiInjector.java
package com.chameleonforensics.chameleon;

import android.app.Activity;
import android.graphics.Typeface;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.HashMap;
import java.util.Map;

public class UiInjector {

    private static final int GREY = 0xFF888888;
    private static final int BLUE = 0xFF1565C0;

    private static final Map<String, TextView> latestTriggerViews = new HashMap<>();
    private static final Map<String, String> latestTriggerTs = new HashMap<>();

    public static class RowRefs {
        public final String className;
        public final TextView statusView;
        public final TextView triggerView;

        RowRefs(String className, TextView statusView, TextView triggerView) {
            this.className = className;
            this.statusView = statusView;
            this.triggerView = triggerView;
        }
    }

    public static RowRefs[] attach(Activity a) {
        latestTriggerViews.clear();
        latestTriggerTs.clear();

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

            TextView triggerStatus = new TextView(a);
            triggerStatus.setTypeface(Typeface.MONOSPACE);
            triggerStatus.setTextSize(13f);
            triggerStatus.setTextColor(GREY);
            triggerStatus.setVisibility(View.GONE);
            col.addView(triggerStatus);

            setLatestTriggerText(triggerStatus, false, null);

            latestTriggerViews.put(cls, triggerStatus);
            rows[i] = new RowRefs(cls, status, triggerStatus);
        }

        return rows;
    }

    public static void resetLatestTrigger(TextView tv) {
        if (tv == null) return;

        tv.post(() -> {
            tv.setVisibility(View.VISIBLE);

            String latestTs = null;
            for (Map.Entry<String, TextView> e : latestTriggerViews.entrySet()) {
                if (e.getValue() == tv) {
                    latestTs = latestTriggerTs.get(e.getKey());
                    break;
                }
            }

            if (latestTs != null && !latestTs.isEmpty()) {
                setLatestTriggerText(tv, true, latestTs);
            } else {
                setLatestTriggerText(tv, false, null);
            }
        });
    }

    public static void markTriggered(String className, String ts) {
        latestTriggerTs.put(className, ts);

        TextView tv = latestTriggerViews.get(className);
        if (tv == null) return;

        tv.post(() -> {
            setLatestTriggerText(tv, true, ts);
        });
    }

    private static void setLatestTriggerText(TextView tv, boolean triggered, String ts) {

        if (triggered && ts != null) {

            // Align timestamp under the "L" of "Latest"
            String prefix = "↳ Latest trigger:";
            String indent = "  "; // matches visual alignment under "Latest"

            String text = prefix + "\n" + indent + ts;

            tv.setText(text);
            tv.setTextColor(BLUE);

        } else {

            // Keep single-line when not triggered
            tv.setText("↳ Latest trigger: Yet to be triggered");
            tv.setTextColor(GREY);
        }

        tv.setPadding(dp(tv, 24), 0, 0, 0);
    }

    private static int dp(View v, int value) {
        return (int) (value * v.getResources().getDisplayMetrics().density + 0.5f);
    }
}