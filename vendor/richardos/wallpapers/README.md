# RichardOS WallpaperPicker2 partner resources

This is a resource-only partner APK for the LineageOS 24.0 WallpaperPicker2
implementation. Its system broadcast receiver makes the package discoverable
through `com.android.launcher3.action.PARTNER_CUSTOMIZATION`.

WallpaperPicker2's legacy partner resource reader expects:

- a `string-array` named `partner_wallpapers`;
- one full-size drawable for each array item;
- a matching thumbnail drawable with the `_small` suffix.

The PNG resources are generated from the three RichardOS SVG masters by
`scripts/install-wallpaper-picker.sh`. Run that helper before Soong parses
the tree. The generated full-size images and thumbnails are intentionally not
committed as binary artifacts.

The APK is system_ext and platform-signed by the build. It does not replace
WallpaperPicker2 or implement its own picker UI. The existing WallpaperPicker2
renders the bundled images and applies them through WallpaperManager.

This integration is source-level only. Build the `RichardOSWallpapers`
module, verify that WallpaperPicker2 discovers all three assets, and test
home/lock/both destinations before claiming device support.
