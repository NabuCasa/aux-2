# Home Assistant Connect AUX-2

This is the ESPHome source code of the Home Assistant Connect AUX-2.

If you need to re-install the firmware, [use this installer](https://firmware.nabucasa.com/install/aux-2/).

## Repository layout

- `packages/aux-2.yaml`: the core configuration, imported when you take control of the device.
- `packages/factory.yaml`: the factory overlay (provisioning, Improv, signed OTA updates).
- `connect-aux-2.yaml`: the factory build target, combining both packages.
