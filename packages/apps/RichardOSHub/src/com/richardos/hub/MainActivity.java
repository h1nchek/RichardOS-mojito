package com.richardos.hub;

import android.app.Activity;
import android.app.AlertDialog;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.content.SharedPreferences;

public class MainActivity extends Activity {
    private static final String PREFS = "richardos_hub";
    private static final String KEY_ACCENT = "accent";
    private LinearLayout content;
    private SharedPreferences prefs;
    private int accent;

    private static final String[] PALETTE_NAMES =
            {"Ocean", "Sage", "Orchid", "Ember", "Graphite", "Rose"};
    private static final String[] PALETTE_VALUES =
            {"#527FA8", "#638D78", "#9474B8", "#BB7055", "#626875", "#B56F83"};

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        accent = prefs.getInt(KEY_ACCENT, Color.parseColor("#527FA8"));
        getWindow().setStatusBarColor(darken(accent));
        getWindow().setNavigationBarColor(Color.BLACK);
        showHome();
    }

    private int dp(float value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private int darken(int color) {
        return Color.rgb((int)(Color.red(color)*0.72),
                (int)(Color.green(color)*0.72), (int)(Color.blue(color)*0.72));
    }

    private TextView text(String value, int size) {
        TextView v = new TextView(this);
        v.setText(value);
        v.setTextSize(size);
        v.setTextColor(Color.WHITE);
        v.setPadding(dp(4), dp(8), dp(4), dp(8));
        return v;
    }

    private void base(String subtitle) {
        ScrollView scroll = new ScrollView(this);
        content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(22), dp(18), dp(22), dp(28));
        content.setBackgroundColor(Color.rgb(18, 19, 23));
        scroll.addView(content);
        setContentView(scroll);
        content.addView(text("RichardOS", 30));
        TextView sub = text(subtitle, 14);
        sub.setTextColor(Color.LTGRAY);
        content.addView(sub);
    }

    private void card(String title, String description, View.OnClickListener action) {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(16), dp(12), dp(16), dp(12));
        box.setBackgroundColor(Color.rgb(35, 37, 43));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                -1, -2);
        lp.setMargins(0, dp(7), 0, dp(7));
        content.addView(box, lp);
        box.addView(text(title, 18));
        TextView detail = text(description, 13);
        detail.setTextColor(Color.LTGRAY);
        box.addView(detail);
        if (action != null) box.setOnClickListener(action);
    }

    private void showHome() {
        base("Your Android. Your rules.");
        card("Monet & Themes", "Wallpaper colors, RichardOS palettes and custom accent",
                v -> showThemes());
        card("Status Bar & Quick Settings", "Clock, battery and Quick Settings options",
                v -> showStatus());
        card("Root & System", "Read-only system and root diagnostics",
                v -> showSystem());
        card("Lock Screen", "Clock, privacy and lock screen preferences",
                v -> showLock());
        card("About RichardOS", "Device: " + Build.DEVICE + "  •  Android " + Build.VERSION.RELEASE,
                null);
    }

    private void showThemes() {
        base("Monet & Themes");
        card("Wallpaper colors", "Use Android's wallpaper-derived dynamic colors. Framework integration pending.", null);
        for (int i = 0; i < PALETTE_NAMES.length; i++) {
            final int color = Color.parseColor(PALETTE_VALUES[i]);
            final String name = PALETTE_NAMES[i];
            card(name, PALETTE_VALUES[i] + (accent == color ? "  •  Selected" : ""),
                    v -> {
                        accent = color;
                        prefs.edit().putInt(KEY_ACCENT, accent).apply();
                        getWindow().setStatusBarColor(darken(accent));
                        showThemes();
                    });
        }
        card("Custom accent", "Enter a hexadecimal color such as #527FA8", v -> customAccent());
        card("Reset", "Return to the default RichardOS palette", v -> {
            accent = Color.parseColor(PALETTE_VALUES[0]);
            prefs.edit().putInt(KEY_ACCENT, accent).apply();
            getWindow().setStatusBarColor(darken(accent));
            showThemes();
        });
        back();
    }

    private void customAccent() {
        EditText input = new EditText(this);
        input.setSingleLine(true);
        input.setHint("#RRGGBB");
        new AlertDialog.Builder(this).setTitle("Custom accent")
                .setView(input).setNegativeButton("Cancel", null)
                .setPositiveButton("Apply", (d, w) -> {
                    try {
                        accent = Color.parseColor(input.getText().toString().trim());
                        prefs.edit().putInt(KEY_ACCENT, accent).apply();
                        getWindow().setStatusBarColor(darken(accent));
                        showThemes();
                    } catch (IllegalArgumentException e) {
                        new AlertDialog.Builder(this).setMessage("Invalid color. Use #RRGGBB.")
                                .setPositiveButton("OK", null).show();
                    }
                }).show();
    }

    private void showStatus() {
        base("Status Bar & Quick Settings");
        card("Integration status", "Controls are not wired to SystemUI yet. This screen is an implementation placeholder.", null);
        card("Planned", "Clock and date • battery display • Quick Settings density and labels", null);
        back();
    }

    private void showSystem() {
        base("Root & System");
        card("Device", Build.DEVICE, null);
        card("Model", Build.MODEL, null);
        card("Android release", Build.VERSION.RELEASE, null);
        card("Build fingerprint", Build.FINGERPRINT, null);
        card("Root status", "Not determined by this first app build. No root actions are performed.", null);
        back();
    }

    private void showLock() {
        base("Lock Screen");
        card("Integration status", "Lock screen controls require framework/SystemUI integration and are not active yet.", null);
        card("Planned", "Clock styles • notification privacy • supported shortcuts", null);
        back();
    }

    private void back() {
        Button button = new Button(this);
        button.setText("Back");
        button.setOnClickListener(v -> showHome());
        content.addView(button);
    }
}
