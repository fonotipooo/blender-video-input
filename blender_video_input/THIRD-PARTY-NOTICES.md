# Third-party components

The Live Video Input Python code is distributed under GPL-3.0-or-later; see LICENSE.txt. Third-party components retain their own copyright and license notices.

## Spout

SpoutLibrary.dll is bundled for Windows x64 only, from the upstream Spout 1.12.0 portable distribution. SHA256: f9cad1eb9934257f47f4219f74dd83cbb781b2b0689e9faf2a76cd7fa75a406c. Its ABI is pinned; do not replace it with an arbitrary DLL. The reference header is leadedge/Spout2 commit a26f74a11d43ef74778d73b6741d6805462702c0, with the older library's vtable differences accounted for in the binding.

Spout is copyright Lynn Jarvis and contributors, under the BSD 2-Clause license. License text and the applicable original copyright notice are included under native/windows-x64/. Source: https://github.com/leadedge/Spout2

## Syphon / syphon-python / PyObjC

The unchanged wheels in wheels/ provide syphon-python 0.2.0 and PyObjC core, Cocoa and Metal 12.2.2 for Python 3.13, universal Intel/Apple Silicon. They are extracted locally only when Syphon is selected on macOS. No dependency installer or network download runs in Blender.

syphon-python is copyright Florian Bruggisser, under MIT. Source: https://github.com/cansik/syphon-python . Syphon.framework is copyright Tom Butterworth, Anton Marini and contributors, under a BSD license. The wheel retains the upstream license texts.

PyObjC is copyright Ronald Oussoren and contributors, under MIT. Source: https://github.com/ronaldoussoren/pyobjc . Its license text is also included in this package's licenses/ folder.

## NDI

NDI runtime binaries and NDI Tools are not redistributed in this kit. Recipients obtain their own official matching runtime or SDK from https://ndi.video/ and must follow its terms. NDI is a registered trademark of Vizrt NDI AB. The add-on links to NDI near its input selector, and the user guide includes its attribution and download reference.
