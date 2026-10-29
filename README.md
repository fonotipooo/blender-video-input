# Museum room + Live Video Input for Blender

Rehearse your live visuals on the included museum walls and floor, using Spout (Windows), Syphon (Mac), NDI, local media or a moving test pattern.

**[Download the complete museum kit](https://github.com/fonotipooo/blender-video-input/releases/tag/v0.3.1-museum-kit)** · **[10-step setup](START-HERE.md)** · **[Resolume / TouchDesigner / OBS](SENDING-VIDEO.md)** · **[AI installation prompt](AI-INSTALL-PROMPT.md)**

## Start here

Download **Museum-room-kit-0.3.1-beta.zip** from the linked release and extract the outer ZIP. In Blender, open **Preferences > Add-ons**, open the menu at the top right and choose **Install from Disk**. Select the inner **Blender-Video-Input-0.3.1-beta.zip**, keep it compressed, and enable **Live Video Input**.

On Mac, use the Blender build matching your processor: **Apple Silicon** for M-series Macs or **Intel** for Intel Macs. The beta targets **Blender 4.5 LTS / Python 3.11** and **Blender 5.2 LTS / Python 3.13**. Its bundled Syphon dependencies load locally for the matching Python version; there is no dependency download or terminal installation step. See the validation status below before relying on a particular combination.

Open **Museum-room.blend**. Its seven room surfaces are selected: in the 3D View press **N**, choose **Video Input > Apply to selected objects**, switch to **Material Preview**, then choose **Test pattern > Connect**. Check that the pattern moves, then disconnect and set up your live sender. **Preview quality defaults to Half** and **Maximum FPS to 15** to reduce Blender's copying load; these controls do not change the room geometry or UV mapping.

The room keeps its existing mesh, transforms and UV mapping. The shared scene contains a neutral packed mapping reference, with no performance visuals, user media, Score project, personal logs or technical-rider PDF. Version 0.3.1 adds Blender 4.5 compatibility and matching Mac dependencies; the earlier 0.3.0 release is retained. The original 0.3.0 kit also works on the tested Mac with Blender 5.2.

## What is included

- **Museum-room.blend**: full-scale walls and floor, existing UVs and camera views.
- **Museum-mapping-reference.png**: a neutral atlas for testing alignment.
- **Blender-Video-Input-0.3.1-beta.zip**: installable extension with offline Mac dependencies.
- Short installation instructions, sender guides, troubleshooting, AI installation prompt and checksums.

Install the inner add-on ZIP, not the outer kit or GitHub's automatic Source code archive. The add-on also works with your own geometry. Save a separate working copy before changing materials in your own scene.

## Geometry and canvas

| Item | Size |
| --- | --- |
| Modeled room bounding dimensions | Approximately **28.69 × 16.99 × 6 m** |
| Museum preview canvas | **4019 × 2899 pixels** |
| Full venue canvas | **8038 × 5798 pixels** |

Half the width and height means **one quarter of the pixels**, while physical geometry stays full scale. This preview is useful for checking placement, proportions and transitions. The room contains walls and floor; separate stage/gauze screens are not modeled. See [geometry details](Museum-geometry-details.json) and [more about the dimensions](LEARN-MORE.md#museum-dimensions-and-resolution).

The project's current live delivery plan is one **8038 × 5798 NDI stream at 30 fps**, following the supplied pixelmap. The venue handles projector routing, warping, edge blending and synchronization. Local Spout/Syphon preview is a separate workflow. Keep the complete atlas, masks, orientation and unused black regions when preparing your sender.

The receiver limits **displayed preview images to 16 megapixels**; Spout also limits incoming textures to 16 megapixels. The 4019 × 2899 atlas is about 11.65 megapixels and fits this limit. The full venue canvas is about 46.6 megapixels and is outside this kit's supported full-resolution preview target. Set up the full-size venue output separately in your production app and confirm delivery requirements with the organizers.

## Compatibility — beta

Targets: **Blender 4.5 LTS / Python 3.11** and **Blender 5.2 LTS / Python 3.13**. Bundled Syphon dependencies require **macOS 12+** and include Intel/Apple Silicon code with Python-specific PyObjC wheels. Other Blender/Python versions have not been validated.

| System | Live inputs | Version 0.3.1 validation |
| --- | --- | --- |
| Windows x64 | Spout, NDI | Pending; historical 0.3.0 checks are recorded separately |
| macOS Apple Silicon | Syphon, NDI | Installed-ZIP tests pass on macOS 15.7.8, Apple M2 Pro, Blender 4.5.12 and 5.2.3; synthetic native senders |
| macOS Intel | Syphon, NDI | Hardware testing pending |
| Linux x64 | NDI | Hardware testing pending |

On the tested **Apple M2 Pro (arm64), macOS 15.7.8**, the installed 0.3.1 ZIP passed with **Blender 4.5.12 / Python 3.11.11** and **Blender 5.2.3 / Python 3.13.13**. Checks covered the offline moving pattern, local 4019 × 2899 image and movie, applying the material to all seven room surfaces, unchanged geometry/UVs, disable/re-enable, and changing **320 × 180 synthetic Syphon and NDI frames with reconnect**. A separate Blender 5.2 Syphon check received a **4019 × 2899 BGRA** source at **2010 × 1450 Half preview**, with correct colors and orientation.

NDI needs a separately installed official matching runtime. The Mac tests explicitly selected the existing Resolume NDI runtime; it is not bundled. The test pattern and local reference work without a sender or NDI runtime. **Actual Resolume, TouchDesigner and OBS end-to-end integrations have not been tested in this pass.** Synthetic protocol reception does not establish sustained frame rates, long-session stability or venue playback. See [VALIDATION.md](VALIDATION.md) for observed results and remaining limits.

## Help

Start the sender using [Resolume, TouchDesigner or OBS instructions](SENDING-VIDEO.md), choose the matching input/source in Blender, and **Connect**. For errors use **Advanced and troubleshooting > Show error log** or **Export support log**. Logs stay local until you choose to share them; review source names and network details first. Report problems in [Issues](https://github.com/fonotipooo/blender-video-input/issues) using [BUG-REPORT.md](BUG-REPORT.md).

## Source and notices

Add-on source is in [blender_video_input/](blender_video_input/), under **GPL-3.0-or-later**; see [LICENSE.txt](LICENSE.txt). Bundled dependencies retain their licenses in [THIRD-PARTY-NOTICES.md](blender_video_input/THIRD-PARTY-NOTICES.md). The code license does not replace existing rights in the museum model. The room is a preview model, not a certified architectural survey.

NDI runtime binaries and NDI Tools are not bundled. Obtain the matching runtime/SDK from [NDI](https://ndi.video/). NDI® is a registered trademark of Vizrt NDI AB.
