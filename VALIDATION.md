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
