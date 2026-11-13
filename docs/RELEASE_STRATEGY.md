# RichardOS release strategy

## 0.9.0 pre-release — GSI first

The 0.9.0 track is an experimental ARM64 GSI focused on development, compatibility research and tester feedback. It is not feature-complete and must not be represented as a stable daily-use operating system.

A pre-release artifact may be published only after:
- the exact upstream build target is confirmed;
- a real image is successfully built;
- artifact integrity and checksum are verified;
- known limitations and compatibility requirements are documented;
- internal validation has been completed.

Use identifiers such as 0.9.0-pre.1, 0.9.0-pre.2 and so on. Never create a release tag or announce a downloadable image before the corresponding artifact exists.

## 1.0.0 stable — device port

The Redmi Note 10 (mojito) port is deferred to the 1.0.0 stable release cycle. It remains a separate device-specific target, not part of the universal GSI configuration.

The 1.0.0 milestone requires a successful build, device-specific validation, documented hardware status, reproducible artifacts and release notes. The version number is a target, not a promise that the release is ready.

## Version truthfulness

Repository checks and documentation are not an Android build. Do not claim a bootable image, supported device list, fixed hardware bug or stable release without corresponding evidence.
