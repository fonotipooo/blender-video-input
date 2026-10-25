"""macOS Metal receiver using the bundled syphon-python 0.3.0 wheels.

Native Mac integration must be validated on Mac hardware before a stable release.
"""
import sys
import numpy as np

_directory = None

def directory():
    global _directory
    if sys.platform != 'darwin':
        raise RuntimeError('Syphon is available on macOS only. Choose NDI on this computer.')
    if _directory is None:
        import syphon
        _directory = syphon.SyphonServerDirectory()
        _directory.run_loop_interval = .001
    return _directory

def discover(wait_ms=0):
    return [(f'{s.app_name}: {s.name}', s.uuid) for s in directory().servers]

def close_finder():
    global _directory
    if _directory is not None:
        _directory.close()
        _directory = None

class Receiver:
    def __init__(self, name, uuid=''):
        import syphon
        matches = [s for s in directory().servers if s.uuid == uuid or (not uuid and f'{s.app_name}: {s.name}' == name)]
        if len(matches) != 1:
            raise RuntimeError('Syphon source disappeared or has an ambiguous name. Refresh sources.')
        self.client = syphon.SyphonMetalClient(matches[0])

    def frame(self, downsample=1, flip=True):
        directory().update_run_loop()
        if not self.client.is_valid:
            raise RuntimeError('Syphon sender disconnected.')
        if not self.client.has_new_frame:
            return None
        texture = self.client.new_frame_image
        if texture is None:
            return None
        from syphon.utils.numpy import copy_mtl_texture_to_image
        w, h = texture.width(), texture.height()
        if w <= 0 or h <= 0 or w*h > 100_000_000:
            raise RuntimeError('Invalid or oversized Syphon frame.')
        pixels = copy_mtl_texture_to_image(texture)
        fmt = texture.pixelFormat()
        if fmt == 80:  # Metal.MTLPixelFormatBGRA8Unorm
            pixels = pixels[..., [2, 1, 0, 3]]
        elif fmt != 70:  # Metal.MTLPixelFormatRGBA8Unorm
            raise RuntimeError('Syphon requires an RGBA8 or BGRA8 sender texture.')
        if flip:
            pixels = pixels[::-1]
        return np.ascontiguousarray(pixels[::downsample, ::downsample]), (w, h)

    def close(self):
        self.client.stop()
