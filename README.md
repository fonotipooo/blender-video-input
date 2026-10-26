# Museum room + Live Video Input for Blender

Preview your live visuals on the included museum room, using Spout (Windows), Syphon (Mac), NDI, local media or a moving test pattern.

**[Download the complete museum kit](https://github.com/fonotipooo/blender-video-input/releases/tag/v0.3.0-museum-kit)** · **[10-step setup](START-HERE.md)** · **[Resolume / TouchDesigner / OBS](SENDING-VIDEO.md)** · **[AI installation prompt](AI-INSTALL-PROMPT.md)**

## Start here

Download **Museum-room-kit-0.3.0-beta.zip** from the linked release and extract the outer ZIP. Install the inner **Blender-Video-Input-0.3.0-beta.zip** using **Preferences > Add-ons > Install from Disk**, and enable **Live Video Input**. Open **Museum-room.blend**. Its seven room surfaces are selected: press **N > Video Input > Apply to selected objects**, switch to **Material Preview**, and choose **Test pattern > Connect**.

The kit reuses the existing working room geometry and the previously tested 0.3.0 add-on. Neither the mesh nor the UV mapping nor the add-on code was rebuilt. The scene copy has old connection settings and private paths removed. It contains a neutral packed mapping reference, with no performance visuals, user media, Score project, personal logs or technical-rider PDF.

## What is included

- **Museum-room.blend**: full-scale walls and floor, existing UVs and camera views.
- **Museum-mapping-reference.png**: a neutral atlas for testing alignment.
- **Blender-Video-Input-0.3.0-beta.zip**: unchanged installable extension.
- Short installation instructions, sender guides, troubleshooting, AI installation prompt and checksums.

Install the inner add-on ZIP, not the outer kit or GitHub's automatic Source code archive. The add-on also works with your own geometry.

## Geometry and canvas

| Item | Size |
| --- | --- |
| Modeled room bounding dimensions | Approximately **28.69 × 16.99 × 6 m** |
| Museum preview canvas | **4019 × 2899 pixels** |
| Venue master canvas | **8038 × 5798 pixels** |

Half the width and height means **one quarter of the pixels**, while physical geometry stays full scale. This is useful for preview performance; it does not replace the full-resolution venue master. The room contains walls and floor; separate stage/gauze screens are not modeled. See [geometry details](Museum-geometry-details.json) and [more about the dimensions](LEARN-MORE.md#museum-dimensions-and-resolution).

The supplied venue rider specifies one 8038 × 5798 NDI stream for the venue. Local Spout/Syphon preview is a separate workflow. The receiver caps preview images and Spout inputs at 16 megapixels, so the full 46.6-megapixel venue master is not a supported full-resolution preview target. Use the half-size canvas for this kit.

## Compatibility — beta

Target: **Blender 5.2 LTS**. Mac Syphon dependencies require macOS 12+ and Blender's Python 3.13.

| System | Live inputs | Validation |
| --- | --- | --- |
| Windows x64 | Spout, NDI | Prior functional and installed-ZIP checks pass |
| macOS Intel / Apple Silicon | Syphon, NDI | Implemented; hardware testing pending |
| Linux x64 | NDI | Implemented; hardware testing pending |

NDI needs a separately installed official matching runtime. The test pattern works offline. Full-resolution sustained performance is not benchmarked. The installation check of this newly published room kit is tracked in [VALIDATION.md](VALIDATION.md).

## Help

Start the sender using [Resolume, TouchDesigner, then OBS instructions](SENDING-VIDEO.md), choose the matching input/source in Blender, and Connect. For errors use **Advanced and troubleshooting > Show error log** or **Export support log**. Logs stay local until you choose to share them; review source names and network details first. Report problems in [Issues](https://github.com/fonotipooo/blender-video-input/issues) using [BUG-REPORT.md](BUG-REPORT.md).

## Source and notices

Add-on source is in [blender_video_input/](blender_video_input/), under **GPL-3.0-or-later**; see [LICENSE.txt](LICENSE.txt). Bundled dependencies retain their licenses in [THIRD-PARTY-NOTICES.md](blender_video_input/THIRD-PARTY-NOTICES.md). The code license does not replace existing rights in the museum model. The room is a preview model, not a certified architectural survey.

NDI runtime binaries and NDI Tools are not bundled. Obtain the matching runtime/SDK from [NDI](https://ndi.video/). NDI® is a registered trademark of Vizrt NDI AB.
