# More options and troubleshooting

These instructions accompany **Live Video Input 0.3.1 beta**. It targets Blender **4.5 LTS / Python 3.11** and **5.2 LTS / Python 3.13**. The installed ZIP passed on **Apple M2 Pro arm64 / macOS 15.7.8**, with **Blender 4.5.12 / Python 3.11.11** and **Blender 5.2.3 / Python 3.13.13**, using offline/local media and moving synthetic Syphon/NDI senders with reconnect. Actual Resolume, TouchDesigner and OBS integrations and sustained frame rates were not tested. Consult [VALIDATION.md](VALIDATION.md) for the complete results and remaining limits. The original v0.3.0 release remains available unchanged.

## Destination

Select one or more mesh objects and choose **Apply to selected objects**. The add-on creates an emission material with an Image Texture node and assigns it to those meshes. It uses their existing UVs. You can undo the assignment.

To use an existing material instead, open **Advanced and troubleshooting**, choose **Material**, and enter the exact **Texture node** name of an existing Image Texture node. Its shader links and UVs should already be set up for your scene. Changing a node or material name may require updating this selection.

Use **Material Preview** or **Rendered** viewport shading to see the video material. Material Preview is a useful first check. This add-on supplies image textures; it does not route audio.

## Other inputs

- **Test pattern**: a built-in animated source, with no sender or external video runtime needed.
- **Image or video file**: choose a file and click **Load**. Play Blender's timeline for movies. Codec support follows Blender; movies use automatic texture refresh and looping.
- **Spout**: Windows only, with the pinned library bundled in the add-on.
- **Syphon**: Mac only, requiring macOS 12+. Universal Intel/Apple Silicon dependencies are bundled for Python 3.11 and 3.13, matching the two target Blender versions. The worker selects the matching Python ABI locally; no dependency installer or network download runs in Blender. See VALIDATION.md for current Mac test results.
- **NDI**: local or network video. Install the official compatible runtime/SDK separately.

## NDI runtime setup

Get a runtime or SDK for your operating system and processor from [NDI](https://ndi.video/) / [NDI SDK](https://ndi.video/for-developers/ndi-sdk/). The add-on searches common locations and the system linker. If automatic detection fails, browse to the actual library under **Advanced and troubleshooting > NDI library**, then disconnect and reconnect.

| System | Library |
| --- | --- |
| Windows x64 | Processing.NDI.Lib.x64.dll |
| macOS Intel / Apple Silicon | libndi.dylib with matching architecture |
| Linux x64 | x86-64 libndi.so and its required system dependencies |

The Mac validation selected an existing Resolume NDI runtime explicitly; no NDI runtime was bundled or installed by the kit. That check used a synthetic NDI sender, rather than an actual Resolume composition.

Keep network senders and receivers on a reachable LAN. Allow the apps through the firewall if your system asks. The library selection is stored with the scene, so choose a matching library again if moving the scene to another operating system.

NDI® is a registered trademark of Vizrt NDI AB.

## Performance and orientation

**Preview quality defaults to Half**, and **Maximum FPS defaults to 15**. Half reduces each incoming dimension for the image displayed in Blender; the source dimensions and room UVs stay unchanged. Lower these settings, or the sender's resolution/FPS, to reduce copying work. The sender can run at 30 fps while the receiver updates its preview at a lower rate. This beta copies frames through CPU memory; it is not a zero-copy GPU path. No sustained atlas-size frame rate is promised. The Blender 5.2 Mac check received a 4019 × 2899 BGRA Syphon source as a 2010 × 1450 Half preview with correct colors and orientation; this was a functional check, not a throughput benchmark.

The **displayed preview image** is capped at 16 megapixels. Spout incoming textures are also capped at 16 megapixels. Syphon and NDI can accept larger source frames before downsampling within their own bounds, but this is not a supported full-resolution venue-preview workflow. Use 8-bit RGBA/BGRA for Spout/Syphon; HDR and float textures are not supported. Use **Flip vertically** to correct upside-down input after checking the labeled mapping reference.

## Common problems

| Problem | Check |
| --- | --- |
| No video on the object | Select a mesh, apply the video material, switch to Material Preview, and try Test pattern first. |
| Empty Source list | Start the sender and playback; choose the matching protocol and refresh. Spout/Syphon require the same computer. |
| Waiting for frames | The source may be visible while not publishing video. Check its output connection and playback. |
| Missing NDI runtime | Install the official matching runtime and select its library if necessary. |
| Syphon dependency/version error on Mac | Use macOS 12+ and the native Blender 4.5 / Python 3.11 or Blender 5.2 / Python 3.13 build matching your processor. Reinstall the complete inner 0.3.1 ZIP; do not mix files from different releases. |
| Unsupported pixel format | Set the sender to 8-bit RGBA/BGRA. |
| Choppy preview | Reduce preview quality/FPS and sender resolution/FPS. |
| Worker not responding | Disconnect, inspect the log, and reconnect. The add-on only stops its own capture process. |
| Destination node missing | Choose a valid Image Texture node or apply a new video material. |

## Logs

Choose **Show error log** or **Export support log** in Advanced. Show error log opens Blender's Text Editor; use **Shift+F5** to return that area to the 3D View. Reports include versions, protocol, source names, dimensions and available error traces. Home-directory paths are masked, but other machine/network details can remain. Review before sharing.

Logs stay on your computer until you choose to share them. The add-on has no automatic log upload. See [BUG-REPORT.md](BUG-REPORT.md).

## Museum dimensions and resolution

Use the provided Museum-room.blend. Its walls and floor keep the existing geometry, transforms and all UV layers. Seven room surfaces are preselected; Apply to selected objects assigns the receiver material without rebuilding them. **View > Cameras > Active Camera** shows the interior camera, including on Mac keyboards without a number pad; **Numpad 0** also works. The packed reference works offline. To show the same reference through the receiver, choose Image or video file, load Museum-mapping-reference.png, then return to your live input when ready.

The modeled bounding dimensions are approximately 28.69 × 16.99 × 6 m. The preview atlas is 4019 × 2899. The project's current full live-delivery plan is one **8038 × 5798 NDI stream at 30 fps**, following the supplied pixelmap. The venue handles projector routing, warping, edge blending and synchronization; confirm your own entry's requirements with the organizers. Half width/height gives one quarter of the pixels, preserving normalized UV placement. Smaller video outputs are useful for connection checks; use the same aspect ratio for meaningful mapping checks. Keep the complete atlas, supplied masks, positions, orientation and unused black regions. Retain independent editable surface masters in your production project. The included moving 1280 × 720 test pattern checks frame reception and is not a museum atlas.

The half-resolution atlas has about 11.65 megapixels and fits the 16-megapixel displayed-preview limit even at Full preview quality. Half, the default, further reduces the image displayed in Blender without changing the incoming atlas or UV layout. The full venue canvas has about 46.6 megapixels: do not treat this receiver as a full-resolution venue preview or sender. Keep the venue master in your production app, and arrange its required NDI output separately with venue technicians. The original technical-rider PDF is not bundled. Separate stage/gauze screen geometry is not included.
