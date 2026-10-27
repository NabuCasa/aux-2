# Backfilled SBOMs

These releases were built before the firmware pipeline produced a software bill of materials (SBOM). Each SBOM here was reconstructed afterwards by rebuilding the release with the exact inputs its original CI build used, checking the rebuild against the firmware that was published and signed, and then running [esp-idf-sbom](https://github.com/espressif/esp-idf-sbom) on the rebuild. Releases built since the SBOM step was added (#53) get their SBOM from the pipeline and are not in this folder.

`publish-backfilled-sbom.yml` uploads each folder's `firmware-esp32s3.sbom.spdx` and `firmware-esp32s3.sbom.cdx.json` next to that release's firmware on `https://firmware.nabucasa.com/aux-2/<version>/`. Every SBOM also says in its document comment (SPDX `DocumentComment`, CycloneDX `metadata.properties` `nabucasa:reconstructed`) that it was reconstructed, from which inputs, and which published firmware it matches.

## Scope

All releases a shipped unit can be running: the two factory images and every later release on the production update channel.

- `2026.8.10`: factory image for the first batch (1,000 units).
- `2026.9.0`: factory image for the second batch (14,000 units).
- `2026.9.1` to `2026.10.3`: installed over the air from `https://firmware.nabucasa.com/aux-2/manifest.json`.

Earlier releases (`2026.8.0` to `2026.8.9`) are not covered. Shipped units start at `2026.8.10` or later, only update from that channel, and have OTA downgrade protection enabled, so they cannot install them.

## Build inputs

The original builds used ESPHome's `dev` branch and some `@main` or pull request sources, and their logs record only the ESPHome version (such as `2026.10.0-dev`) and the ESP-IDF version. Each commit below is the newest commit of that source before the build step started, from the archived CI logs. The verification below confirms them.

| Release | ESPHome `dev` | ESP-IDF | External components |
|---|---|---|---|
| 2026.8.10 | `169c0550119a96f1677029b1478542c4e38390a3` | 5.5.5 | `improv_serial` from ESPHome PR #17598 at `167c6a3e485373a262dabdfed747890a12905573`; `w5500_link_monitor` from `components/` at the tag |
| 2026.9.0 | `ab800dc09dbe2d1eb1ed1ee8f091282561e0ccc4` | 5.5.5 | `usb_uart` from ESPHome PR #18969 at `2c7d80dd9873bd490e65898ade42c51da4f0ead7`; `w5500_link_monitor` from aux-2 at `1f1db29849d41cff731982696b3581bd9315f47a` |
| 2026.9.1 | `a00d241cad0e39f54b045ce7994d4b1b0c506e74` | 5.5.5 | `w5500_link_monitor` from aux-2 at `6cb065914c9deea6b76beab73e16e5934a6d72ca` |
| 2026.10.0 | `42edfe0681cdd5023c7285dbd2fbfc53c0f5c40e` | 5.5.5 | `w5500_link_monitor` from aux-2 at `599c865066bf8c0c0a7204aa1bc1fb5fbd5d60d7` |
| 2026.10.1 | `7aeed8455e47b8f0cf804492081b02488ffa190e` | 5.5.5 | `w5500_link_monitor` from aux-2 at `01bc450d353c70b00a3417884cee12b6a8720d0f` |
| 2026.10.2 | `01524a2ffde8ddfab9b8d6d1e892408292227769` | 5.5.6 | `w5500_link_monitor` from aux-2 at `655357f24b8837ea5f965fdf9fdfd3273256c3d8` |
| 2026.10.3 | `45c7fd52148a83735f13690fb3d3673cc0dcec1f` | 5.5.6 | `w5500_link_monitor` from aux-2 at `815fa2a3cb715caa8c8dcd33e21e1776924762ba` |

In every case the aux-2 `@main` source resolved to the tag commit itself.

## Verification

Each release was rebuilt from its tag with the sources above pinned to those commits, `FW_VERSION` set to the release and the production channel, and the production signing-key digests (read from the published image's own signature blocks) as the trust anchor. The rebuilt unsigned app was then compared with the published signed app (`firmware-esp32s3.ota.bin`, which is the unsigned app followed by the signature sector). `verification.txt` in each folder has the output.

| Release | Factory image sha256 | Bytes that differ | Text strings (rebuilt / published) | Result |
|---|---|---|---|---|
| 2026.8.10 | `a6f30406774dd5fb44ab29d544fafdbfb6e03f4d991e5af7dbc112df25fcd28a` | 336,487 (see below) | 6,184 / 6,184 | MATCH |
| 2026.9.0 | `776e1f9299cb7647e131d248a2187b636f1fb0fc0eb337f22972ebda0e6af022` | 341,940 (see below) | 6,294 / 6,294 | MATCH |
| 2026.9.1 | `69882e583a294281632aa82e8fcc6a86fee5bb861b4bcffb97474fc2bd62f3f0` | 82 | 6,305 / 6,305 | MATCH |
| 2026.10.0 | `3fe8fe9210b8a6e859ec17b789129fc595f2c1bdc59e8867c0856d1f41c8a9a1` | 82 | 6,333 / 6,333 | MATCH |
| 2026.10.1 | `4b3d3512e7e2643efe162a219059938732ab3e2c153e7474e08db00b7d514f5b` | 81 | 6,333 / 6,333 | MATCH |
| 2026.10.2 | `7456c0eb91e5bcadf59020acd5eec41d4ff109b60a1f3ad2897231da14710fa6` | 86 | 6,689 / 6,689 | MATCH |
| 2026.10.3 | `9f20f49b21903f6a79cf101226feb5a73165bd31d6c072f4c925b91ecbf42447` | 84 | 6,695 / 6,695 | MATCH |

From `2026.9.1` on, the rebuild is identical to the published app except for about 80 bytes: the embedded build time, and the hashes that cover it (the app ELF SHA-256 in the app descriptor, and the image checksum and SHA-256 at the end).

`2026.8.10` and `2026.9.0` still contained the Opus codec, whose source paths ESP-IDF embeds in log messages with a prefix that depends on the build directory (`/./` in CI, `/../` in the rebuild). That shifts everything after the first such string, so many bytes differ at the byte level. With that prefix and the build time normalized, every text string in the image (log, version and format strings, and function names) matches. A different ESPHome, component or library version changes these strings; comparing the `2026.8.10` rebuild with the `2026.9.0` image, for example, reports different mDNS function names.

## Known vulnerabilities

`vuln-report.json` in each folder is the `esp-idf-sbom check` report against the US National Vulnerability Database, run on 2026-10-27. None of the releases has a vulnerability that applies to it.

- In every release, nine CVEs match a package by version and are marked not applicable by the package's own manifest or Espressif's exclusion list, each with its reason (FreeRTOS MPU and TrustZone ports, a RISC-V libgloss issue in newlib, an mbedTLS issue specific to Clang, two issues already fixed in ESP-IDF).
- From `2026.10.2` on, ESP-IDF's `bt` component is in the build, and esp-idf-sbom lists its NimBLE submodule (Apache NimBLE 1.6.0) even though this firmware uses the Bluedroid host. Two NimBLE CVEs that ESP-IDF does not yet exclude, CVE-2026-45812 and CVE-2026-45813, are recorded as not affected with the justification `component_not_present`: no NimBLE source is compiled and no NimBLE symbol is linked. `excluded_cves.yaml` in those folders holds the statement, as used when the SBOM was generated.
- Packages without an NVD identifier (ESPHome and its components, Improv, most ESP-IDF components) cannot be checked against the NVD and are reported as skipped.

## Tools

`tools/` holds the scripts used, so each step can be repeated:

- `write_manifests.py` writes the `sbom.yml` files that ESPHome writes into a build since esphome/esphome#21454, which these older ESPHome versions did not.
- `compare_app.py` compares a rebuilt app with the published signed app byte by byte.
- `verify_strings.py` compares their text strings with the build directory prefix and build time normalized.
