# RichardOS 0.9.0 GSI — tester intake

This page collects compatibility information for the experimental 0.9.0 GSI track. **No installable RichardOS image is available yet.** This is not an installation guide.

## Device information

Record only information needed to assess compatibility:

- Manufacturer and exact model number
- Device codename, if known
- Android version and current vendor build version
- CPU/userspace architecture, if already known
- Whether the manufacturer documents Project Treble support
- Whether this is a spare test device (not a daily-use phone)

Mark unknown values as unknown; do not guess. A 64-bit processor alone does not establish GSI compatibility.

## Test stages

- Stage 0 — interest and intake: collect device details only.
- Stage 1 — compatibility review: maintainers assess the device as a possible candidate.
- Stage 2 — internal validation: maintainers verify an actual build and its release notes.
- Stage 3 — limited pre-release feedback: testers report against a named 0.9.0-pre.N build and checksum, once one exists.

Do not ask testers to change device security settings, erase data or modify their phones during intake. Any future real-device test needs informed adult oversight and a device-specific recovery plan.

## Bug report checklist

- Exact RichardOS build identifier and checksum (once published)
- Exact device model/codename
- Android and vendor build versions
- Expected behaviour and actual behaviour
- Reproduction frequency
- Screenshot or redacted log excerpt

Remove phone numbers, account names, email addresses, serial numbers, IMEI, precise location and other personal identifiers before sharing logs.

## Known limitations

- A GSI does not include every manufacturer's hardware customization.
- Camera, fingerprint, NFC, mobile data, VoLTE, audio and sensors may vary by device.
- One device passing a test does not prove compatibility with another device.
- A bug is not fixed until the fix is present in a named build and verified.
