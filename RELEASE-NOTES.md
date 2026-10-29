# Museum room kit — 0.3.1 beta

This update adds **Blender 4.5 LTS / Python 3.11** compatibility alongside **Blender 5.2 LTS / Python 3.13**, with bundled Python-specific Mac dependencies loaded offline. The original 0.3.0 kit also works on the tested Mac with Blender 5.2; this update extends support to Blender 4.5. It retains the existing full-scale room geometry, transforms, UV mapping and neutral reference image.

Download **Museum-room-kit-0.3.1-beta.zip** from [v0.3.1-museum-kit](https://github.com/fonotipooo/blender-video-input/releases/tag/v0.3.1-museum-kit) and extract it. Install its inner **Blender-Video-Input-0.3.1-beta.zip** in Blender, open **Museum-room.blend**, and follow [START-HERE.md](START-HERE.md). The seven room surfaces are preselected; click **Apply to selected objects** to connect them to the receiver. **Preview quality defaults to Half**, with a default receiver rate of **15 fps**.

On Mac, choose the Blender build matching your processor. Syphon dependencies require macOS 12+; NDI still needs an official matching runtime installed separately. The guides include Mac keyboard camera navigation and protocol choices for Resolume, TouchDesigner and OBS.

Room: about **28.69 × 16.99 × 6 m**. Preview canvas: **4019 × 2899**. Full venue canvas: **8038 × 5798**. Half width and height gives one quarter of the pixels; geometry stays full scale. Displayed preview images and incoming Spout textures are limited to 16 megapixels. This kit is for rehearsal; sustained atlas-size throughput and full-size venue operation require separate verification.

**Installed-ZIP Mac validation passed** on **Apple M2 Pro arm64 / macOS 15.7.8**, using **Blender 4.5.12 / Python 3.11.11** and **Blender 5.2.3 / Python 3.13.13**:

- Registration, disable/re-enable and applying the video material to all seven room surfaces; geometry and UVs remained identical.
- Moving offline test pattern, local 4019 × 2899 image and local movie.
- Changing 320 × 180 frames from synthetic native Syphon and NDI senders, with disconnect/reconnect on both Blender versions.
- On Blender 5.2, a 4019 × 2899 BGRA Syphon sender produced a 2010 × 1450 Half preview with correct colors and orientation.

The NDI checks used an existing Resolume runtime selected explicitly; it is not bundled. **Actual Resolume, TouchDesigner and OBS end-to-end integration and sustained frame rates were not tested.** Intel Mac, Linux and Windows 0.3.1 runtime checks remain pending. See [VALIDATION.md](VALIDATION.md) for detailed results and limits.

Only the room, neutral reference, receiver, dependencies, licenses and guides are included. Performance visuals, personal files, old sender settings and the technical-rider PDF are excluded.

## Previous release retained

The **v0.3.0-museum-kit** release and its assets remain available unchanged. Its historical Windows x64 / Blender 5.2.3 LTS installation and reception checks are documented in VALIDATION.md. Those results apply to version 0.3.0; they do not certify this update or native Mac/Linux operation.
