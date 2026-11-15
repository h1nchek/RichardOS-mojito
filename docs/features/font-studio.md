# RichardOS Font Studio

Status: a launcher-based preview/import prototype now exists in `vendor/richardos/fontstudio`; Android compilation and on-device testing are still pending. System-wide font switching is not implemented.

Target release: 1.0.0 (device/system integration milestone). The feature must remain separate from the generic GSI/device-port split: the Settings UI may be shared, but the privileged font backend must be integrated and tested on each supported product.

## User experience

Add **RichardOS → Appearance → Font Studio** with:

- Built-in font families that are bundled with the ROM and have compatible redistribution licenses.
- A preview sample showing Latin, Cyrillic, numerals, punctuation, and common symbols.
- Import for user-owned `.ttf` and `.otf` files using Android's document picker.
- Metadata display (family name, style, supported glyph coverage where practical).
- Apply, reset to system default, and restore-last-known-good actions.
- Clear errors for malformed, unsupported, or incomplete font families.

## Safety and compatibility requirements

1. Never overwrite files in `/system/fonts` or mutate the read-only system partition at runtime.
2. Treat imported font files as untrusted input. Enforce a conservative file-size limit, copy to app-private staging storage, validate with Android's font parser, and reject malformed files before they reach the privileged backend.
3. Do not execute, load as code, or request broad storage access for font files.
4. Keep the current active font until the complete replacement family has been validated and staged.
5. Apply changes atomically through a dedicated privileged system service / supported font configuration mechanism. Settings UI must not gain arbitrary root or shell execution.
6. Keep a last-known-good configuration and provide an automatic rollback path if applying a font fails.
7. Preserve fallback coverage for Latin, Cyrillic, CJK, emoji, symbols, and device-required glyphs. A single imported face must not silently replace the entire fallback chain.
8. Check font licenses before bundling presets. Imported fonts remain user-provided and are not redistributed by RichardOS.
9. Accessibility: retain readable preview, TalkBack labels, and a simple reset path.

## Architecture

### Settings UI

Extend the existing native Settings RichardOS dashboard with a Font Studio preference and dedicated fragment. The UI owns browsing, preview, import, and user-facing state. It must not directly write system font files or claim that a preview-only import has changed the system.

### Import pipeline

- Use `ACTION_OPEN_DOCUMENT` with MIME filters for TrueType and OpenType font files, while allowing extension-based fallback for providers with incomplete MIME metadata.
- Stream the selected document into app-private staging; do not trust the display name or extension alone.
- Enforce size limits and parse the font before accepting it.
- Record a content hash and parsed family/style metadata.
- Keep imported fonts in private app storage until the privileged backend accepts a validated staged asset.

### Privileged apply backend (required for system-wide changes)

Use Android's supported runtime font-management path rather than writing `/system/fonts`. AOSP provides the `FontManager` system service (Android 12+) and `FontManagerService`; the service checks the privileged `UPDATE_FONTS` permission for font configuration updates.

**LineageOS 24.0 source inspection (verified):** `FontManagerService` is present at `services/core/java/com/android/server/graphics/fonts/FontManagerService.java`. Its Binder API exposes `getFontConfig()`, `updateFontFamily(List<FontUpdateRequest>, int baseVersion)`, and `updateFontFallbacks(List<FontUpdateRequest>)`; it enforces `android.permission.UPDATE_FONTS`. The request type in this branch is `android.graphics.fonts.FontUpdateRequest` (not the newer/different `FontFamilyUpdateRequest` / `FontFileUpdateRequest` names), so code must follow this branch's exact API.

The service creates its updatable font directory only when fs-verity is supported and safe mode is off. It loads trusted certificates from `config_fontManagerServiceCerts`, verifies detached PKCS#7 signatures against fs-verity digests, and returns `RESULT_ERROR_FONT_UPDATER_DISABLED` when the updater is unavailable. Updates also use a base config version to reject stale writes. These are hard prerequisites, not optional implementation details.

Therefore, the app-private preview/import app must not call a guessed hidden API directly or be granted broad root access. Before implementing a backend, verify the exact `UPDATE_FONTS` protection level and allowlist policy, the product's fs-verity support, the trusted certificate resource and signing-key custody, the signed-font format, and the API's request parceling/lifecycle. Only then implement a narrowly scoped platform-signed updater/backend that supplies signed font assets and the current base version. Do not add an unsigned arbitrary-font bypass or weaken fs-verity checks.

The backend must preserve the platform fallback configuration and support rollback/reset. Verify that the target LineageOS build actually enables the FontManager service and updater flow before choosing this route. Do not assume that changing a Settings key or replacing a file immediately changes Android's system font.

### State model

Suggested states: `DEFAULT`, `PREVIEWING`, `STAGED`, `APPLYING`, `APPLIED`, `ROLLING_BACK`, `ERROR`.

Persist only the selected preset/import identifier and backend-reported state. Never persist raw document URIs as globally accessible paths.

## Delivery plan

### Phase A — preview/import prototype (implemented in source; build/test pending)
- Add a launcher-accessible Font Studio prototype app.
- Preview built-in Android typeface families and Latin/Cyrillic sample text.
- Import TTF/OTF into app-private staging with a 20 MiB limit and Typeface parser validation.
- Persist the last preview selection and preserve the previous imported font if replacement fails.
- Imports are **Preview only**; no system-wide apply is exposed.

Remaining Phase A work: integrate the screen into the native Settings dashboard, improve family/style metadata and accessibility, and run Soong plus on-device tests.

### Phase B — platform integration
- Inspect LineageOS 24.0 `FontManager`, `FontManagerService`, `FontUpdater`, `UPDATE_FONTS`, and signature validation implementation.
- Confirm that the service and trusted updater are enabled in the target build; record exact source paths and API signatures.
- Implement a platform-signed updater/backend using this branch's `FontUpdateRequest` API only after verifying fs-verity availability, trusted certificate provisioning, permission policy, and signing-key custody.
- Add atomic apply, reset, rollback, and per-user persistence.
- Verify that changes affect Settings, SystemUI, launcher, and third-party apps consistently where platform policy permits.

### Phase C — validation
- Unit tests for file validation, metadata, limits, and state transitions.
- Integration tests for import, apply, reboot persistence, reset, rollback, and malformed files.
- Manual tests for Latin/Cyrillic and fallback glyph coverage.
- Build Settings and platform components; test on an emulator and each supported device before marking the feature stable.

## Acceptance criteria

- Invalid or oversized files are rejected without changing the active font.
- Valid TTF/OTF files can be previewed safely.
- Applying a font is unavailable until the privileged backend is present.
- When backend support lands, apply/reset are atomic, survive reboot, and can roll back.
- No runtime writes to `/system/fonts`, no shell/root execution from Settings, and no loss of fallback glyph coverage.
- Feature status is accurately represented in release notes; a UI screen alone is not considered system-wide font support.
