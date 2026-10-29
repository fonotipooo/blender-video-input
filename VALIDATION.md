# Validation - Live Video Input beta

## Historical Windows validation — 0.3.0

Checked on Windows x64 with Blender 5.2.3 LTS and its bundled Python 3.13.

- Registration, disable/re-enable and generic selected-object material creation pass.
- Vertex coordinates, transforms and UV data remain unchanged when assigning the video material.
- An unselected mesh sharing the original mesh data remains unaffected by the selected object's assignment.
- The moving 1280 x 720 test pattern, 640 x 360 preview, disconnect and reconnect pass.
- Local movie loading with automatic texture refresh passes; codec support follows Blender.
- Separate synthetic Spout and NDI senders provide changing 320 x 180 frames; reception and disconnect/reconnect pass for both protocols.
- Support reports mask home-directory paths, including JSON-escaped paths.
- The release ZIP installs and enables in an isolated Blender extension repository; the installed copy applies the selected-object material, receives changing test-pattern frames and disconnects cleanly.

These historical Windows results do not certify Mac or Linux operation. See the Mac 0.3.1 results below. Full-resolution sustained throughput, long-session stability and every sender-app integration are not benchmarked or certified. Source discovery alone should not be reported as successful frame reception.

NDI requires a separately installed official matching runtime. The release does not bundle NDI runtime binaries or NDI Tools.

## Museum kit packaging update

The existing room meshes/transforms/UVs were copied intact into a clean scene container to exclude old connection/tool history. A geometry/UV signature matched before and after copying. Only the neutral mapping image is packed, and embedded private path/sender checks pass. Receiver code and its installable 0.3.0 ZIP are unchanged.

**Post-publication installation check: PASSED on Windows x64, Blender 5.2.3 LTS (2026-10-25).**

The museum kit was downloaded from its published GitHub release asset, and its SHA-256 plus the inner installer, room and mapping-image checksums matched. The inner ZIP was installed and enabled through Blender's extension installer in a fresh, isolated extension repository, with separate configuration and a writable test temporary folder.

- Museum-room.blend opens as a normal scene with all seven room surfaces preselected and its interior camera available.
- The existing mesh bounding dimensions remain approximately 28.69 × 16.99 × 6 m; only the neutral 4019 × 2899 reference image is packed.
- Apply to selected objects assigns the receiver material to all seven surfaces.
- The moving test pattern delivers four distinct frames at 1280 × 720 (640 × 360 preview); disconnect and reconnect both pass, with four distinct frames after reconnect.
- The local mapping reference loads at the full 4019 × 2899 half-resolution atlas size.
- Geometry coordinates, transforms and every UV layer match the preserved working-room signature after all checks.
- Support-report home-path masking passes, and the downloaded room renders with the neutral mapping reference.

This is a Windows installation/reception check. It does not certify native Mac/Linux operation, every sender-app combination, sustained high-resolution throughput or venue operation.


## Mac installed-ZIP validation — 0.3.1 (October 29, 2026)

**Passed** on Apple M2 Pro (arm64), macOS 15.7.8:

| Blender | Embedded Python | Install and offline/local media | Native Syphon | Native NDI |
| --- | --- | --- | --- | --- |
| 4.5.12 LTS | 3.11.11 | Passed | Passed | Passed |
| 5.2.3 LTS | 3.13.13 | Passed | Passed | Passed |

Each run installed the release ZIP through Blender's normal extension installer in a separate configuration/repository, opened the downloaded published Museum-room.blend, and applied the material to all seven preselected room surfaces. Tests covered registration, disable/re-enable, the moving offline pattern, local movie automatic-refresh/loop settings, the full 4019 × 2899 reference, and clean disconnect/reconnect.

Independent native synthetic senders provided changing 320 × 180 video frames. Both protocols delivered at least five distinct decoded/uploaded frames before and after reconnect on both Blender versions. RGBA/BGRA channel order and vertical orientation matched the asymmetric source pattern. NDI used the already installed NDI SDK APPLE 5.5.1 runtime from Resolume, selected explicitly; no runtime was installed or bundled.

A separate Blender 5.2 Syphon test received changing **4019 × 2899 BGRA** frames. Default **Half** preview produced **2010 × 1450** pixels (ceiling division for odd dimensions), with correct color and orientation before and after reconnect. This is a bounded functional check, not a sustained 30-fps benchmark. The default receiver maximum is 15 fps.

Coordinates, transforms, polygon topology and every UV layer were identical across all checks and Blender versions. The shared model and mapping PNG remain byte-for-byte identical to the 0.3.0 published assets. Reference renders from both versions were visually inspected. Support reports masked home-directory paths.

The original published **0.3.0** kit was also checksum-verified, installed, and successfully tested on **Mac Blender 5.2.3**, including moving Syphon frames/reconnect, offline/local media and a room render. Version 0.3.1 adds compatibility with Blender 4.5's Python 3.11; it does not imply that 0.3.0 was broken on Mac Blender 5.2.

Five automated dependency checks cover CPython 3.11/3.13 wheel selection, both Mac architectures, unsupported-version errors, and extraction without incompatible native modules. Matching PyObjC/Cocoa/Metal/Syphon imports and the Apple M2 Pro Metal device were checked with both embedded interpreters.

**Limits:** these are local synthetic-protocol checks. Actual Resolume, TouchDesigner and OBS end-to-end workflows, Intel Mac, Linux, Windows 0.3.1, long sessions, sustained atlas-size frame rates, and venue/network/audio synchronization remain unverified. Historical Windows 0.3.0 results above remain specific to that version. The preview receiver does not replace the project's full 8038 × 5798 / 30 fps NDI delivery plan.
