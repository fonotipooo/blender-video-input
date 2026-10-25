# More options and troubleshooting

## Destination

Select one or more mesh objects and choose **Apply to selected objects**. The add-on creates an emission material with an Image Texture node and assigns it to those meshes. It uses their existing UVs. You can undo the assignment.

To use an existing material instead, open **Advanced and troubleshooting**, choose **Material**, and enter the exact **Texture node** name of an existing Image Texture node. Its shader links and UVs should already be set up for your scene. Changing a node or material name may require updating this selection.

Use **Material Preview** or **Rendered** viewport shading to see the video material. Material Preview is a useful first check. This add-on supplies image textures; it does not route audio.

## Other inputs

- **Test pattern**: a built-in animated source, with no sender or external video runtime needed.
- **Image or video file**: choose a file and click **Load**. Play Blender's timeline for movies. Codec support follows Blender; movies use automatic texture refresh and looping.
- **Spout**: Windows only, with the pinned library bundled in the add-on.
- **Syphon**: Mac only, with Python 3.13 universal Mac dependencies bundled. Native Mac testing is pending.
- **NDI**: local or network video. Install the official compatible runtime/SDK separately.

## NDI runtime setup

Get a runtime or SDK for your operating system and processor from [NDI](https://ndi.video/) / [NDI SDK](https://ndi.video/for-developers/ndi-sdk/). The add-on searches common locations and the system linker. If automatic detection fails, browse to the actual library under **Advanced and troubleshooting > NDI library**, then disconnect and reconnect.

| System | Library |
| --- | --- |
| Windows x64 | Processing.NDI.Lib.x64.dll |
| macOS Intel / Apple Silicon | libndi.dylib with matching architecture |
| Linux x64 | x86-64 libndi.so and its required system dependencies |

Keep network senders and receivers on a reachable LAN. Allow the apps through the firewall if your system asks. The library selection is stored with the scene, so choose a matching library again if moving the scene to another operating system.

NDI® is a registered trademark of Vizrt NDI AB.

## Performance and orientation

Lower **Preview quality** or **Maximum FPS** to reduce Blender's image-copying load. Lowering the sender's resolution/FPS also reduces capture work. This beta copies frames through CPU memory; it is not a zero-copy GPU path. Preview-size controls do not change your geometry or UVs.

The displayed preview is capped at 16 megapixels. Spout incoming textures are also capped at 16 megapixels in this beta. Use 8-bit RGBA/BGRA for Spout/Syphon; HDR and float textures are not supported. Use **Flip vertically** for upside-down Spout/Syphon input.

## Common problems

| Problem | Check |
| --- | --- |
| No video on the object | Select a mesh, apply the video material, switch to Material Preview, and try Test pattern first. |
| Empty Source list | Start the sender and playback; choose the matching protocol and refresh. Spout/Syphon require the same computer. |
| Waiting for frames | The source may be visible while not publishing video. Check its output connection and playback. |
| Missing NDI runtime | Install the official matching runtime and select its library if necessary. |
| Unsupported pixel format | Set the sender to 8-bit RGBA/BGRA. |
| Choppy preview | Reduce preview quality/FPS and sender resolution/FPS. |
| Worker not responding | Disconnect, inspect the log, and reconnect. The add-on only stops its own capture process. |
| Destination node missing | Choose a valid Image Texture node or apply a new video material. |

## Logs

Choose **Show error log** or **Export support log** in Advanced. Show error log opens Blender's Text Editor; use **Shift+F5** to return that area to the 3D View. Reports include versions, protocol, source names, dimensions and available error traces. Home-directory paths are masked, but other machine/network details can remain. Review before sharing.

Logs stay on your computer until you choose to share them. The add-on has no automatic log upload. See [BUG-REPORT.md](BUG-REPORT.md).
