# Install and run in 10 steps

1. Open **Blender 4.5 LTS** or **Blender 5.2 LTS**. On Mac, use the **Apple Silicon** build for M-series Macs or the **Intel** build for Intel Macs. Other Blender/Python combinations have not been validated.
2. Download **Museum-room-kit-0.3.1-beta.zip** from the [museum kit release](https://github.com/fonotipooo/blender-video-input/releases/tag/v0.3.1-museum-kit) and extract this outer ZIP.
3. In Blender, open **Preferences > Add-ons**, open the menu at the top right and choose **Install from Disk**.
4. Choose the inner **Blender-Video-Input-0.3.1-beta.zip**, keep it compressed, and enable **Live Video Input**. On Mac its bundled dependencies load offline; no terminal setup is needed.
5. Open the included **Museum-room.blend**. Save a separate working copy if you want to keep your setup.
6. With its room surfaces selected, move the pointer over the 3D View, press **N**, open **Video Input** and click **Apply to selected objects**.
7. Switch the viewport to **Material Preview**. Use **View > Cameras > Active Camera** or **Numpad 0** for the room camera; the menu also works on Mac keyboards without a number pad.
8. Choose **Test pattern > Connect**, check movement, then **Disconnect**. Keep **Preview quality: Half**, the default, for your first test. The default receiver limit is **15 fps**; sender and receiver rates are separate.
9. Follow the [Resolume, TouchDesigner or OBS guide](SENDING-VIDEO.md). On Mac use **Syphon** for Resolume/TouchDesigner or **NDI** for OBS. Start with a small sender output, then use **4019 × 2899** for the complete museum atlas when your app/edition supports it.
10. In Blender, choose the matching input, refresh **Source**, select the sender, and **Connect**. Verify moving frames and the received dimensions, then check disconnect/reconnect. Source discovery alone does not prove reception.

If the surfaces are no longer selected, select the seven meshes **EST, FLOOR, NORD, SUD, WEST 1, WEST 2 and WEST 3** in the Outliner before step 6. These are the included room surfaces; no rebuilding is needed.

The kit targets Blender's Python **3.11** (4.5 LTS) or **3.13** (5.2 LTS). Mac dependencies require **macOS 12+**. NDI requires its own official matching runtime. The installed ZIP passed on **Apple M2 Pro / macOS 15.7.8**, with **Blender 4.5.12 / Python 3.11.11** and **Blender 5.2.3 / Python 3.13.13**: offline/local media and changing synthetic Syphon/NDI frames, including reconnect. Actual Resolume, TouchDesigner and OBS integration, sustained frame rates, Intel Mac, Linux and Windows 0.3.1 remain untested in this pass. See [VALIDATION.md](VALIDATION.md).

**4019 × 2899 is a rehearsal preview.** Keep the full atlas, masks, orientation and unused black regions. The project's current full live-delivery plan remains **8038 × 5798, 30 fps, one NDI stream**; the venue handles projector routing, warping, blending and synchronization.

Click **Disconnect** when finished. For help: **Advanced and troubleshooting > Export support log**. Review the log before sharing it.

[Extra instructions](LEARN-MORE.md) · [AI installation prompt](AI-INSTALL-PROMPT.md) · [Validation](VALIDATION.md)
