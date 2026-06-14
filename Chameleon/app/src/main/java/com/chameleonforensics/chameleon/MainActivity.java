// app/src/main/java/com/chameleonforensics/chameleon/MainActivity.java
package com.chameleonforensics.chameleon;

import android.os.Bundle;
import android.util.Log;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "Chameleon";

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ChameleonForegroundService.start(this);
        Log.i(TAG, "Foreground Service created");

        setContentView(R.layout.activity_main);

        // Base app log — proves stock APK works before smali injection
        Log.i(TAG, "Base MainActivity onCreate reached");
        ReportCore.init(this);

        UiInjector.RowRefs[] rows = UiInjector.attach(this);

        boolean shouldAutoRun = getIntent().getBooleanExtra("autorun", true);
        if (shouldAutoRun) {
            long staggerMs = 600L; // tweak as you like
            AutoRunner.runAllWithStagger(this, rows, staggerMs);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        SpecialPermWaiter.onAppForeground();
    }

    @Override
    protected void onPause() {
        super.onPause();
        SpecialPermWaiter.onAppBackground();
    }

}
