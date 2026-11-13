# RichardOS 0.9.0 GSI compatibility matrix

This matrix tracks research status. It is **not** a list of supported devices.

## Status definitions

- `unknown` — not researched or evidence is missing.
- `researching` — source information is being collected.
- `candidate` — documented requirements appear plausible; no image or device validation is implied.
- `blocked` — a known requirement or incompatibility prevents further consideration.
- `validated` — only use after a named RichardOS build has completed documented testing on the exact model and variant.

## Device records

| Manufacturer | Exact model | Codename | Android/vendor version | Treble evidence | ABI evidence | Review status | Build tested | Device tested | Notes |
|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | unknown | unknown | unknown | no | no | No device is currently validated |

## Review requirements

Before marking a device as a candidate, record evidence for:

1. Exact model number and codename. Similar product names are not sufficient.
2. Project Treble support and the device's vendor interface information.
3. Required system architecture and Binder bitness, using trustworthy device documentation or already available system information.
4. Android launch/version and vendor implementation compatibility.
5. Known device-specific limitations, including camera, audio, radio, sensors, fingerprint and encryption.
6. A device-specific recovery and data-protection plan before any physical-device validation.

A 64-bit CPU or a Treble label by itself does not prove that a particular GSI will work.

## Evidence and privacy

Add links to public manufacturer or Android documentation in the Notes column. Do not collect IMEI, serial number, phone number, account identifiers, precise location or unredacted diagnostic logs. Mark unavailable information as `unknown`; never infer a pass.

## Current project status

- RichardOS 0.9.0 GSI: preparation only.
- Installable RichardOS image: not available.
- Build validation: not completed.
- Device validation: not completed.
- Redmi Note 10 (mojito): reserved as a separate planned device-port target for the 1.0.0 release cycle; it is not a validated GSI device.
