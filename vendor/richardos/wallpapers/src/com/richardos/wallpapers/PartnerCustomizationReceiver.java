package com.richardos.wallpapers;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/**
 * Marker receiver used by WallpaperPicker2 to discover RichardOS partner resources.
 * WallpaperPicker2 reads the partner_wallpapers string-array and matching drawable assets.
 */
public final class PartnerCustomizationReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        // Discovery only. WallpaperPicker2 reads this APK's resources directly.
    }
}
