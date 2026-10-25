# Live Video Input for Blender

A standalone Blender add-on for applying live video textures to selected mesh objects. Receive **Spout** on Windows, **Syphon** on macOS, or **NDI** on the supported platforms. Local images/movies and a moving test pattern are included as input options.

**[Download the beta add-on](https://github.com/fonotipooo/blender-video-input/releases)** · **[10-step setup](START-HERE.md)** · **[Resolume / TouchDesigner / OBS](SENDING-VIDEO.md)** · **[AI installation prompt](AI-INSTALL-PROMPT.md)**

## Quick setup

Install **Blender-Video-Input-0.3.0-beta.zip** from Releases using **Preferences > Add-ons > Install from Disk**, and enable **Live Video Input**. Select a mesh, open **N > Video Input**, click **Apply to selected objects**, and switch the viewport to **Material Preview**. Choose **Test pattern > Connect** to verify reception before configuring a sender.

The release contains **only the add-on**. It does not include a Blender scene, geometry, media files, screenshots, technical riders, personal logs or user project data. Use it with your own scene and UV mapping. GitHub's automatic source archive is for developers; install the named release ZIP above.

## Compatibility - 0.3.0 beta

Target: **Blender 5.2 LTS**. The Mac Syphon dependencies require macOS 12+ and Blender's Python 3.13.

| System | Live inputs | Validation |
| --- | --- | --- |
| Windows x64 | Spout, NDI | Functional checks; see VALIDATION.md |
| macOS Intel / Apple Silicon | Syphon, NDI | Implemented; Mac hardware tests pending |
| Linux x64 | NDI | Implemented; Linux hardware tests pending |

Spout and Syphon connect applications on the same computer. NDI can also receive network video and needs a separately installed official runtime. Full-resolution sustained performance is not benchmarked.

## Controls

- Apply a video material to selected meshes, or choose an existing material and Image Texture node under Advanced.
- Choose an input and source; refresh, connect, or disconnect.
- See actual received and displayed preview dimensions.
- Adjust preview quality, maximum FPS and vertical orientation.
- Show or export local error logs when requesting help.

Applying the material is undoable and changes the material assignments of selected objects. Keep a saved copy of your working scene as usual. Local movie playback follows Blender's timeline and codec support.

## Help

Read [SENDING-VIDEO.md](SENDING-VIDEO.md), in the order **Resolume, TouchDesigner, OBS**, or [LEARN-MORE.md](LEARN-MORE.md). You can also copy the [AI installation prompt](AI-INSTALL-PROMPT.md).

For problems, open **Video Input > Advanced and troubleshooting > Export support log**, review the file, and open a [GitHub issue](https://github.com/fonotipooo/blender-video-input/issues) using [BUG-REPORT.md](BUG-REPORT.md). Logs remain on your computer until you choose to share them. Source names and machine/network details may appear in an exported report.

## Source and licenses

The source is in [blender_video_input/](blender_video_input/). The add-on code uses **GPL-3.0-or-later**; see [LICENSE.txt](LICENSE.txt). Bundled Spout, Syphon and PyObjC dependencies retain their own licenses and notices in [THIRD-PARTY-NOTICES.md](blender_video_input/THIRD-PARTY-NOTICES.md).

NDI runtime binaries and NDI Tools are not bundled. Obtain the official matching runtime or SDK from [NDI](https://ndi.video/). NDI® is a registered trademark of Vizrt NDI AB.
