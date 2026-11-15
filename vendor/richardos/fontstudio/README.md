# RichardOS Font Studio prototype

This is the first runnable prototype of the Font Studio experience.

## What works

- Opens from the Android launcher as **Font Studio**.
- Previews built-in Android typeface families (sans-serif, serif, monospace).
- Imports a user-selected TTF/OTF through the system document picker.
- Copies the selected file into app-private storage with a 20 MiB limit.
- Uses Android's Typeface parser as a validation gate before replacing the previously staged font.
- Restores the last preview selection when the app is reopened.
- Includes Latin and Cyrillic preview text.

## What does not work yet

This prototype changes the typeface **inside Font Studio only**. It does not change Settings, SystemUI, the launcher, or other apps. System-wide font switching needs a separately reviewed platform backend, fallback-chain handling, atomic configuration, rollback, and device testing. No root shell or writes to `/system/fonts` are used.

## Build integration

The module is `RichardOSFontStudio`. It is included in the Redmi Note 10 product through `vendor/richardos/config/branding.mk` and is built as a system_ext app.

After syncing the LineageOS 24.0 tree and applying RichardOS integration, build the device target. The app should appear in the launcher as **Font Studio**.

## Manual test

1. Launch Font Studio.
2. Switch between System default, Roboto / Sans, Serif, and Monospace.
3. Import a known-good TTF and then an OTF file.
4. Verify the Latin and Cyrillic sample changes.
5. Restart the app and verify the last selection is restored.
6. Try a non-font file and an oversized file; both should be rejected without replacing the active preview.
