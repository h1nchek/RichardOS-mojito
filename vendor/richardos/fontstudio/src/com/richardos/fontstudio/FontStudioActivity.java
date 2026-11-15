/*
 * Copyright (C) 2026 RichardOS
 * Licensed under the Apache License, Version 2.0.
 */
package com.richardos.fontstudio;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.database.Cursor;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.IOException;

public class FontStudioActivity extends Activity {
    private static final int REQUEST_FONT = 4102;
    private static final long MAX_FONT_BYTES = 20L * 1024L * 1024L;
    private static final String PREFS = "font_studio";
    private static final String KEY_SELECTION = "selection";
    private static final String CUSTOM_FILE = "custom-font";

    private TextView status;
    private TextView preview;
    private File customFont;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        customFont = new File(getFilesDir(), CUSTOM_FILE);
        buildUi();
        restoreSelection();
    }

    private void buildUi() {
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = dp(24);
        root.setPadding(pad, pad, pad, pad);
        scroll.addView(root);

        TextView title = new TextView(this);
        title.setText("RichardOS Font Studio");
        title.setTextSize(26);
        title.setTypeface(Typeface.create("sans-serif", Typeface.BOLD));
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("Choose a typeface or preview your own TTF / OTF file.");
        subtitle.setTextSize(14);
        subtitle.setPadding(0, dp(8), 0, dp(20));
        root.addView(subtitle);

        TextView previewTitle = new TextView(this);
        previewTitle.setText("LIVE PREVIEW");
        previewTitle.setTextSize(12);
        previewTitle.setLetterSpacing(0.08f);
        root.addView(previewTitle);

        preview = new TextView(this);
        preview.setText("Aa Bb Gg 123\nRichardOS — Твой Android. Твои правила.\nСъешь ещё этих мягких французских булок.");
        preview.setTextSize(23);
        preview.setLineSpacing(dp(5), 1f);
        preview.setPadding(dp(16), dp(18), dp(16), dp(18));
        preview.setBackgroundColor(0xFFF0ECE2);
        preview.setTextColor(0xFF24272D);
        LinearLayout.LayoutParams previewParams =
                new LinearLayout.LayoutParams(-1, -2);
        previewParams.setMargins(0, dp(8), 0, dp(18));
        root.addView(preview, previewParams);

        status = new TextView(this);
        status.setTextSize(13);
        status.setPadding(0, 0, 0, dp(12));
        root.addView(status);

        addButton(root, "System default", v -> selectPreset("sans-serif", "System default"));
        addButton(root, "Roboto / Sans", v -> selectPreset("sans-serif", "Roboto / Sans"));
        addButton(root, "Serif", v -> selectPreset("serif", "Serif"));
        addButton(root, "Monospace", v -> selectPreset("monospace", "Monospace"));
        addButton(root, "Import TTF / OTF", v -> openFontPicker());

        TextView note = new TextView(this);
        note.setText("Prototype: fonts are previewed inside this app only. System-wide font replacement is not implemented.");
        note.setTextSize(12);
        note.setPadding(0, dp(18), 0, 0);
        root.addView(note);

        setContentView(scroll);
    }

    private void addButton(LinearLayout parent, String label, View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(label);
        button.setAllCaps(false);
        button.setOnClickListener(listener);
        LinearLayout.LayoutParams params =
                new LinearLayout.LayoutParams(-1, -2);
        params.setMargins(0, dp(4), 0, dp(4));
        parent.addView(button, params);
    }

    private void selectPreset(String family, String label) {
        Typeface typeface = Typeface.create(family, Typeface.NORMAL);
        preview.setTypeface(typeface);
        saveSelection("preset:" + family);
        status.setText("Previewing: " + label);
    }

    private void openFontPicker() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        intent.putExtra(Intent.EXTRA_MIME_TYPES, new String[] {
                "font/ttf", "font/otf", "application/x-font-ttf",
                "application/x-font-otf", "application/octet-stream"
        });
        startActivityForResult(intent, REQUEST_FONT);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQUEST_FONT || resultCode != RESULT_OK
                || data == null || data.getData() == null) {
            return;
        }
        Uri uri = data.getData();
        String displayName = queryDisplayName(uri);
        try {
            importAndPreview(uri);
            saveSelection("custom");
            status.setText("Previewing imported font: " + displayName);
        } catch (IOException | RuntimeException e) {
            status.setText("Could not load this font. Choose a valid TTF or OTF file.");
            Toast.makeText(this, "Font import failed", Toast.LENGTH_LONG).show();
        }
    }

    private void importAndPreview(Uri uri) throws IOException {
        File temporary = new File(getFilesDir(), CUSTOM_FILE + ".tmp");
        long total = 0;
        try (InputStream input = getContentResolver().openInputStream(uri);
             FileOutputStream output = new FileOutputStream(temporary)) {
            if (input == null) {
                throw new IOException("Unable to open selected document");
            }
            byte[] buffer = new byte[8192];
            int count;
            while ((count = input.read(buffer)) != -1) {
                total += count;
                if (total > MAX_FONT_BYTES) {
                    throw new IOException("Font file exceeds size limit");
                }
                output.write(buffer, 0, count);
            }
            output.getFD().sync();
        } catch (IOException e) {
            temporary.delete();
            throw e;
        }

        if (total == 0) {
            temporary.delete();
            throw new IOException("Empty font file");
        }

        // Typeface parsing is the validation gate. Keep the active font untouched
        // unless the candidate can actually be parsed.
        Typeface candidate;
        try {
            candidate = Typeface.createFromFile(temporary);
        } catch (RuntimeException e) {
            temporary.delete();
            throw new IOException("Unsupported or malformed font", e);
        }

        File backup = new File(getFilesDir(), CUSTOM_FILE + ".bak");
        if (backup.exists() && !backup.delete()) {
            temporary.delete();
            throw new IOException("Unable to clear previous backup");
        }
        boolean hadPrevious = customFont.exists();
        if (hadPrevious && !customFont.renameTo(backup)) {
            temporary.delete();
            throw new IOException("Unable to stage previous font for rollback");
        }
        if (!temporary.renameTo(customFont)) {
            temporary.delete();
            if (hadPrevious) {
                backup.renameTo(customFont);
            }
            throw new IOException("Unable to commit staged font");
        }
        if (backup.exists()) {
            backup.delete();
        }
        preview.setTypeface(candidate);
    }

    private String queryDisplayName(Uri uri) {
        String name = "custom font";
        try (Cursor cursor = getContentResolver().query(
                uri, new String[] { OpenableColumns.DISPLAY_NAME },
                null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (index >= 0) {
                    String value = cursor.getString(index);
                    if (value != null && !value.trim().isEmpty()) {
                        name = value;
                    }
                }
            }
        } catch (RuntimeException ignored) {
            // The provider may not expose metadata; the content itself is validated.
        }
        return name;
    }

    private void restoreSelection() {
        SharedPreferences prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        String selection = prefs.getString(KEY_SELECTION, "preset:sans-serif");
        if ("custom".equals(selection) && customFont.isFile()) {
            try {
                preview.setTypeface(Typeface.createFromFile(customFont));
                status.setText("Previewing previously imported font");
                return;
            } catch (RuntimeException ignored) {
                customFont.delete();
            }
        }
        String family = selection.startsWith("preset:")
                ? selection.substring("preset:".length()) : "sans-serif";
        preview.setTypeface(Typeface.create(family, Typeface.NORMAL));
        status.setText("Previewing system font: " + family);
    }

    private void saveSelection(String selection) {
        getSharedPreferences(PREFS, MODE_PRIVATE)
                .edit().putString(KEY_SELECTION, selection).apply();
    }

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }
}
