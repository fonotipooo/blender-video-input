# Install and run in 10 steps

1. Install **Blender 5.2 LTS**.
2. Download **Museum-room-kit-0.3.0-beta.zip** from Releases and extract it.
3. In Blender: **Preferences > Add-ons > Install from Disk**.
4. Choose the inner **Blender-Video-Input-0.3.0-beta.zip**, keep it compressed, and enable **Live Video Input**.
5. Open the included **Museum-room.blend**.
6. With its room surfaces selected, press **N > Video Input > Apply to selected objects**.
7. Switch the viewport to **Material Preview**; use **Numpad 0** for the room camera if needed.
8. Choose **Test pattern > Connect**, check movement, then **Disconnect**.
9. Set up [Resolume, TouchDesigner or OBS](SENDING-VIDEO.md); use **4019 × 2899** for the museum atlas when your app/edition supports it.
10. In Blender, choose the matching input, refresh **Source**, select the sender, and **Connect**.

If the surfaces are no longer selected, select the seven meshes EST, FLOOR, NORD, SUD, WEST 1, WEST 2 and WEST 3 in the Outliner before step 6. These are the actual included room surfaces; no rebuilding is needed.

Click **Disconnect** when finished. For help: **Advanced and troubleshooting > Export support log**.

[Extra instructions](LEARN-MORE.md) · [AI installation prompt](AI-INSTALL-PROMPT.md) · [Validation](VALIDATION.md)
