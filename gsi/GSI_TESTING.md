# RichardOS GSI — tester intake

This page is for collecting compatibility information. It is **not** an installation guide. No RichardOS GSI build is currently available.

## Before accepting a device

Record the following without asking testers to change device security settings:

- Manufacturer and exact model number
- Device codename, if already known
- Current Android version
- Current vendor/build version (from Settings)
- CPU/userspace architecture, if known
- Whether the manufacturer documents Project Treble support
- Whether the device is a spare test device or a daily-use device

A 64-bit processor by itself is not enough. GSI compatibility depends on Treble implementation, vendor interface compatibility, partition layout and other device-specific details. Mark unknown values as **unknown**; do not guess.

## Test stages

- **Stage 0 — intake:** collect device details only.
- **Stage 1 — compatibility review:** maintainers assess whether the device is a plausible candidate.
- **Stage 2 — internal validation:** maintainers verify a build and its release notes before any wider testing.
- **Stage 3 — limited feedback:** testers report only against a named build and checksum.

Do not ask testers to unlock, erase, modify or flash a phone as part of this intake. Never describe an unbuilt image as ready. Early testing carries a real risk of data loss or device failure, so any future real-device testing needs informed adult oversight, a spare device and a device-specific recovery plan.

## Bug report checklist

Include:
- RichardOS build ID and checksum (if a verified build exists)
- Exact device model/codename
- Android and vendor build versions
- Expected behaviour
- Actual behaviour
- Reproduction frequency
- Relevant screenshot or redacted log excerpt

Remove phone numbers, account names, email addresses, serial numbers, IMEI, precise location and other personal identifiers before sharing logs.

## Known limitations

- A GSI does not include every manufacturer's hardware customization.
- Camera, fingerprint, NFC, mobile data, VoLTE, audio and sensors may vary by device.
- One device passing a test does not prove compatibility with another device of the same brand.
- No bug should be marked fixed until the fix is present in a named build and verified.
