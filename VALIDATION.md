# Validation - Live Video Input 0.3.0 beta

Checked on Windows x64 with Blender 5.2.3 LTS and its bundled Python 3.13.

- Registration, disable/re-enable and generic selected-object material creation pass.
- Vertex coordinates, transforms and UV data remain unchanged when assigning the video material.
- An unselected mesh sharing the original mesh data remains unaffected by the selected object's assignment.
- The moving 1280 x 720 test pattern, 640 x 360 preview, disconnect and reconnect pass.
- Local movie loading with automatic texture refresh passes; codec support follows Blender.
- Separate synthetic Spout and NDI senders provide changing 320 x 180 frames; reception and disconnect/reconnect pass for both protocols.
- Support reports mask home-directory paths, including JSON-escaped paths.
- The release ZIP installs and enables in an isolated Blender extension repository; the installed copy applies the selected-object material, receives changing test-pattern frames and disconnects cleanly.

Mac Syphon and Linux operation are implemented but still need hardware validation. Full-resolution sustained throughput, long-session stability and every sender-app integration are not benchmarked or certified. Source discovery alone should not be reported as successful frame reception.

NDI requires a separately installed official matching runtime. The release does not bundle NDI runtime binaries or NDI Tools.

## Museum kit packaging update

The existing room meshes/transforms/UVs were copied intact into a clean scene container to exclude old connection/tool history. A geometry/UV signature matched before and after copying. Only the neutral mapping image is packed, and embedded private path/sender checks pass. Receiver code and its installable 0.3.0 ZIP are unchanged.

**Post-publication installation check: pending.** This page will be updated after downloading and installing the published kit.
