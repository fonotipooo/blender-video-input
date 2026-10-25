# Send video to Blender

Choose your app: **Resolume**, **TouchDesigner**, or **OBS**. A 1280 x 720, 30 fps, 8-bit test output is a useful starting point; choose your own composition size after checking reception.

## Resolume - Windows or Mac

1. Open **Composition > Settings**. Start with **1280 x 720**, **8-bit** color depth, and play a composition.
2. In **Output**, enable **Texture Sharing (Spout)** on Windows or **Texture Sharing (Syphon)** on Mac.
3. In Blender, choose **Spout** or **Syphon**, refresh **Source**, and select the Resolume **Composition** sender. Its label may include **Arena** or **Avenue**.
4. Click **Connect**.

Resolume includes this output feature. Both applications must run on the same computer. [Official Resolume instructions](https://resolume.com/support/en/syphonspout).

## TouchDesigner - Windows or Mac

1. Connect your finished composition to a **Syphon Spout Out TOP**. Start with an upstream **1280 x 720** texture.
2. In its **Common** page, choose **Use Input** resolution and **8-bit fixed (RGBA)** pixel format.
3. Turn **Active** on, set **Sender Name** to **Video Preview**, and keep playback/network cooking active.
4. In Blender, choose **Spout** on Windows or **Syphon** on Mac, refresh, select **Video Preview**, and **Connect**.

Both applications must run on the same computer. Respect your TouchDesigner edition's resolution limits. NDI Out TOP is another route when available; receive it with NDI in Blender. [Official TouchDesigner instructions](https://derivative.ca/UserGuide/Syphon_Spout_Out_TOP).

## OBS on Windows - Spout

1. Close OBS, install the matching Windows [OBS Spout2 plug-in](https://github.com/Off-World-Live/obs-spout2-plugin/releases), and reopen OBS.
2. Add your content. Under **Settings > Video**, start with a **1280 x 720** canvas and **30 fps**.
3. Open **Tools > Spout Output Settings**, name the output **Video Preview**, and click **Start**.
4. In Blender: **Spout > Refresh > Video Preview > Connect**.

Keep OBS and Blender on the same GPU. If the Tools menu entry is missing, check plug-in installation. [Developer's output instructions](https://github.com/Off-World-Live-Collaborative/docs.offworld.live/blob/main/obs-spout-plugin/README.md).

## OBS on Windows, Mac or Linux - NDI

1. Install [DistroAV](https://github.com/DistroAV/DistroAV) and its required official NDI runtime, using releases matching your OBS version and operating system. Restart OBS.
2. Add your content and start with **Settings > Video > 1280 x 720, 30 fps**.
3. Open **Tools > DistroAV NDI Settings**. Older versions may say **NDI Output Settings**.
4. Enable **Main Output**, name it **Video Preview**, and confirm.
5. In Blender: **NDI > Refresh > choose the OBS sender > Connect**.

For OBS on Mac, use this NDI route. A Syphon Capture source receives video; it does not itself publish an OBS Syphon output. [Current DistroAV menu labels](https://github.com/DistroAV/DistroAV/blob/master/data/locale/en-US.ini).

## Check reception

Blender should show **Live** and the incoming dimensions. Its displayed preview may be smaller because of the preview-quality setting. Keep the sending app running. Source discovery alone does not prove that frames are arriving.

These app instructions follow the developers' documentation. End-to-end tests with every app/OS combination are still pending; see [VALIDATION.md](VALIDATION.md). For setup options and troubleshooting, read [LEARN-MORE.md](LEARN-MORE.md).

NDI® is a registered trademark of Vizrt NDI AB. [NDI information](https://ndi.video/).
