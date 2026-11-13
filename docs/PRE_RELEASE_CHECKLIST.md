# RichardOS 0.9.0 pre-release checklist

This checklist is a release gate, not evidence that any item has passed. Keep unchecked items unchecked until there is a verifiable result.

## A. Source and target verification

- [ ] Confirm the exact LineageOS source branch and manifest revision.
- [ ] Confirm the generic ARM64 product definition exists in the synced source tree.
- [ ] Confirm the exact lunch target/alias from source; do not infer it from another Android release.
- [ ] Confirm ARM64 userspace and 64-bit Binder settings.
- [ ] Confirm the GSI configuration contains no mojito-only device files.
- [ ] Run repository metadata and documentation checks.

## B. Baseline build evidence

- [ ] Build the unmodified generic baseline in a suitable, reproducible build environment.
- [ ] Record source revision, build configuration and build environment.
- [ ] Confirm the expected output artifact exists and is non-empty.
- [ ] Calculate and independently verify the artifact checksum.
- [ ] Preserve build logs with secrets and personal data removed.

## C. RichardOS integration

- [ ] Add shared RichardOS branding without replacing required upstream platform assets.
- [ ] Integrate one feature at a time on top of the verified baseline.
- [ ] Run available source/configuration checks after each change.
- [ ] Record known issues and distinguish confirmed fixes from unverified hypotheses.

## D. Validation and release notes

- [ ] Review compatibility requirements and known hardware limitations.
- [ ] Complete internal validation appropriate to the available environment.
- [ ] Document exactly which tests were run and their results.
- [ ] Document untested areas explicitly.
- [ ] Prepare release notes with build identifier, source revision and checksum.
- [ ] Review privacy and safety of all included logs, screenshots and examples.

## E. Publication gate

- [ ] A real artifact exists and has been verified.
- [ ] The artifact matches the documented source revision and build identifier.
- [ ] Compatibility claims are supported by exact-model evidence.
- [ ] Recovery and data-loss risks are clearly documented.
- [ ] Maintainer review is complete.
- [ ] Only now create a versioned pre-release such as `0.9.0-pre.1`.

## Current status

No Android image has been built or validated. No installable RichardOS binary is available. Passing repository CI checks does not satisfy the build, device-validation or publication gates above.

The Redmi Note 10 (mojito) remains a separate planned 1.0.0 device-port milestone.
