package com.chameleonforensics.chameleon;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import androidx.core.app.NotificationCompat;

public class ChameleonForegroundService extends Service {

    private static final String CHANNEL_ID = "chameleon_status_channel";
    private static final int STATUS_NOTIFICATION_ID = 1001;
    private static final int TRIGGER_BASE_NOTIFICATION_ID = 2048;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        startForeground(STATUS_NOTIFICATION_ID, buildNotification(this));
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        refreshNotification(this);
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    public static void start(Context context) {
        Intent intent = new Intent(context, ChameleonForegroundService.class);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent);
        } else {
            context.startService(intent);
        }
    }

    public static void refreshNotification(Context context) {
        NotificationManager nm =
                (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);

        if (nm == null) return;

        nm.notify(STATUS_NOTIFICATION_ID, buildNotification(context));
    }

    private static Notification buildNotification(Context context) {
        FeatureStatusStore.Summary s = FeatureStatusStore.getSummary();

        String title = "ChameleonAF Status";
        StringBuilder sb = new StringBuilder();

        sb.append(s.total)
                .append(" features loaded • ")
                .append(s.active)
                .append(" operational");

        if (s.failed > 0) {
            sb.append(" • ")
                    .append(s.failed)
                    .append(" error(s)");
        }

        if (s.waitingPermissions > 0) {
            sb.append(" • ")
                    .append(s.waitingPermissions)
                    .append(" awaiting permissions");
        }

        if (s.waitingRoot > 0) {
            sb.append(" • ")
                    .append(s.waitingRoot)
                    .append(" awaiting root");
        }

        if (s.pending > 0) {
            sb.append(" • ")
                    .append(s.pending)
                    .append(" initialising");
        }

        String text = sb.toString();

        Intent openIntent = new Intent(context, MainActivity.class);
        openIntent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);

        PendingIntent pendingIntent = PendingIntent.getActivity(
                context,
                0,
                openIntent,
                Build.VERSION.SDK_INT >= Build.VERSION_CODES.M
                        ? PendingIntent.FLAG_IMMUTABLE
                        : 0
        );

        NotificationCompat.Builder builder =
                new NotificationCompat.Builder(context, CHANNEL_ID)
                        .setContentTitle(title)
                        .setContentText(text)
                        .setSmallIcon(R.mipmap.ic_launcher) // Change this later for app icon
                        .setContentIntent(pendingIntent)
                        .setOngoing(true)
                        .setOnlyAlertOnce(true)
                        .setPriority(NotificationCompat.PRIORITY_LOW)
                        .setCategory(NotificationCompat.CATEGORY_SERVICE);

        return builder.build();
    }

    public static void showFeatureTriggeredNotification(
            Context context,
            String featureName,
            String timestamp
    ) {
        NotificationManager nm =
                (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);

        if (nm == null) return;

        Intent openIntent = new Intent(context, MainActivity.class);
        openIntent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);

        PendingIntent pendingIntent = PendingIntent.getActivity(
                context,
                featureName.hashCode(),
                openIntent,
                Build.VERSION.SDK_INT >= Build.VERSION_CODES.M
                        ? PendingIntent.FLAG_IMMUTABLE
                        : 0
        );

        String title = "ChameleonAF Anti-Forensic Feature Triggered";
        String displayName = resolveFeatureDisplayName(featureName);
        String text = displayName + " triggered at UTC " + timestamp;

        Notification notification =
                new NotificationCompat.Builder(context, CHANNEL_ID)
                        .setContentTitle(title)
                        .setContentText(text)
                        .setSmallIcon(R.mipmap.ic_launcher)
                        .setContentIntent(pendingIntent)
                        .setAutoCancel(true)
                        .setOnlyAlertOnce(false)
                        .setPriority(NotificationCompat.PRIORITY_DEFAULT)
                        .setCategory(NotificationCompat.CATEGORY_STATUS)
                        .build();

        int notificationId = TRIGGER_BASE_NOTIFICATION_ID + Math.abs(featureName.hashCode() % 1000);
        nm.notify(notificationId, notification);
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;

        NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "Chameleon Status",
                NotificationManager.IMPORTANCE_LOW
        );

        channel.setDescription("Shows active Chameleon feature monitoring status.");

        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm != null) {
            nm.createNotificationChannel(channel);
        }
    }

    private static String resolveFeatureDisplayName(String featureName) {
        if (featureName == null) return "Unknown feature";

        for (int i = 0; i < FeatureRegistry.featureClasses.length; i++) {
            if (featureName.equals(FeatureRegistry.featureClasses[i])) {
                if (i < FeatureRegistry.featureLabels.length
                        && FeatureRegistry.featureLabels[i] != null
                        && !FeatureRegistry.featureLabels[i].isEmpty()) {
                    return FeatureRegistry.featureLabels[i];
                }
                break;
            }
        }

        return featureName;
    }
}