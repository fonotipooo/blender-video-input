"""Small NDI receiver using the NDI runtime already installed on this computer.

The ABI layouts and calls follow the NDI SDK's Find, Recv and structs headers.
This module does not access Blender; all Blender data changes stay on its timer.
"""
import ctypes as C
import os
import time


class Source(C.Structure):
    _fields_ = [('name', C.c_char_p), ('url', C.c_char_p)]


class FindSettings(C.Structure):
    _fields_ = [('show_local', C.c_bool), ('groups', C.c_char_p), ('extra_ips', C.c_char_p)]


class ReceiveSettings(C.Structure):
    _fields_ = [('source', Source), ('color_format', C.c_int),
                ('bandwidth', C.c_int), ('allow_fields', C.c_bool), ('name', C.c_char_p)]


class VideoFrame(C.Structure):
    _fields_ = [('width', C.c_int), ('height', C.c_int), ('fourcc', C.c_int),
                ('fps_n', C.c_int), ('fps_d', C.c_int), ('aspect', C.c_float),
                ('format', C.c_int), ('timecode', C.c_int64),
                ('data', C.POINTER(C.c_uint8)), ('stride', C.c_int),
                ('metadata', C.c_char_p), ('timestamp', C.c_int64)]


_sdk = None
_finder = None
_runtime_path = None


def sdk():
    global _sdk, _runtime_path
    if _sdk is not None:
        return _sdk
    import sys, ctypes.util
    candidates = [os.environ.get("BVI_NDI_RUNTIME", ""), os.environ.get("NDI_RUNTIME_DIR_V6", ""), os.environ.get("NDI_RUNTIME_DIR_V5", "")]
    if os.name == "nt":
        base = os.environ.get("ProgramFiles", "C:/Program Files")
        candidates += [base + "/NDI/NDI 6 Runtime/v6/Processing.NDI.Lib.x64.dll", base + "/NDI/NDI 6 Tools/Runtime/Processing.NDI.Lib.x64.dll"]
    elif sys.platform == "darwin":
        candidates += ["/usr/local/lib/libndi.dylib", "/Library/NDI SDK for Apple/lib/macOS/libndi.dylib"]
    else:
        candidates += [ctypes.util.find_library("ndi"), "/usr/local/lib/libndi.so", "/usr/lib/libndi.so"]
    errors = []
    for path in candidates:
        if not path:
            continue
        if os.path.isdir(path):
            path = os.path.join(path, 'Processing.NDI.Lib.x64.dll' if os.name=='nt' else ('libndi.dylib' if sys.platform=='darwin' else 'libndi.so'))
        if not os.path.isfile(path) and os.path.isabs(path):
            continue
        try:
            lib = C.CDLL(path)
            declarations = {
                'NDIlib_initialize': (C.c_bool, []),
                'NDIlib_find_create_v2': (C.c_void_p, [C.POINTER(FindSettings)]),
                'NDIlib_find_get_current_sources': (C.POINTER(Source), [C.c_void_p, C.POINTER(C.c_uint32)]),
                'NDIlib_find_wait_for_sources': (C.c_bool, [C.c_void_p, C.c_uint32]),
                'NDIlib_find_destroy': (None, [C.c_void_p]),
                'NDIlib_recv_create_v3': (C.c_void_p, [C.POINTER(ReceiveSettings)]),
                'NDIlib_recv_connect': (None, [C.c_void_p, C.POINTER(Source)]),
                'NDIlib_recv_capture_v2': (C.c_int, [C.c_void_p, C.POINTER(VideoFrame), C.c_void_p, C.c_void_p, C.c_uint32]),
                'NDIlib_recv_free_video_v2': (None, [C.c_void_p, C.POINTER(VideoFrame)]),
                'NDIlib_recv_destroy': (None, [C.c_void_p]),
                'NDIlib_recv_get_no_connections': (C.c_int, [C.c_void_p]),
            }
            for name, (result, args) in declarations.items():
                func = getattr(lib, name)
                func.restype, func.argtypes = result, args
            if not lib.NDIlib_initialize():
                raise RuntimeError('NDI could not initialize.')
            _sdk, _runtime_path = lib, path
            return lib
        except Exception as exc:
            errors.append(str(exc))
    raise RuntimeError('NDI runtime missing or incompatible. Install the official NDI runtime/SDK and select its library in Advanced settings. ' + '; '.join(errors))


def discover(wait_ms=0):
    """Return owned UTF-8 strings, never pointers owned by the finder."""
    global _finder
    lib = sdk()
    if _finder is None:
        # Also query loopback, so local senders remain
        # discoverable when multicast discovery is unavailable in the host.
        settings = FindSettings(True, None, b'127.0.0.1')
        _finder = lib.NDIlib_find_create_v2(C.byref(settings))
        if not _finder:
            raise RuntimeError('Could not create the NDI source finder.')
    if wait_ms:
        lib.NDIlib_find_wait_for_sources(_finder, wait_ms)
    count = C.c_uint32()
    sources = lib.NDIlib_find_get_current_sources(_finder, C.byref(count))
    return [(sources[i].name.decode('utf8'),
             sources[i].url.decode('utf8') if sources[i].url else '')
            for i in range(count.value)]


def close_finder():
    global _finder
    if _finder is not None and _sdk is not None:
        _sdk.NDIlib_find_destroy(_finder)
    _finder = None


class Receiver:
    def __init__(self, name, url=''):
        self.lib = sdk()
        # Retain bytes for the full native receiver lifetime.
        self.name_bytes = name.encode('utf8')
        self.url_bytes = url.encode('utf8') if url else None
        self.source = Source(self.name_bytes, self.url_bytes)
        self.settings = ReceiveSettings(self.source, 2, 100, False, b'Blender Video Input')
        self.handle = self.lib.NDIlib_recv_create_v3(C.byref(self.settings))
        if not self.handle:
            raise RuntimeError('Could not create the NDI receiver.')

    def close(self):
        if self.handle:
            self.lib.NDIlib_recv_destroy(self.handle)
            self.handle = None

    def frame(self, downsample=1, byte_pixels=False):
        """Read without waiting, copy RGBA before releasing native buffers.

        Blender stores rows from bottom to top; NDI delivers top to bottom.
        Honor row padding and reject unsupported pixel formats explicitly.
        """
        import numpy as np
        latest = None
        deadline = time.perf_counter() + 0.012
        try:
            for _ in range(8):
                frame = VideoFrame()
                kind = self.lib.NDIlib_recv_capture_v2(self.handle, C.byref(frame), None, None, 0)
                if kind == 1:
                    if latest is not None:
                        self.lib.NDIlib_recv_free_video_v2(self.handle, C.byref(latest))
                    latest = frame
                elif kind == 4:
                    raise RuntimeError('The NDI source disconnected.')
                elif kind == 0:
                    break
                if time.perf_counter() >= deadline:
                    break
            if latest is None:
                return None
            w, h = latest.width, latest.height
            if not latest.data or w <= 0 or h <= 0 or w*h > 100_000_000:
                raise RuntimeError('Invalid NDI frame.')
            code = latest.fourcc.to_bytes(4, 'little').decode('ascii', errors='replace')
            if code not in ('RGBA', 'RGBX', 'BGRA', 'BGRX'):
                raise RuntimeError('Unsupported NDI pixel format: ' + code)
            stride = latest.stride or w*4
            if stride < w*4:
                raise RuntimeError('Invalid NDI row stride.')
            raw = np.ctypeslib.as_array(latest.data, shape=(h*stride,))
            pixels = raw.reshape(h, stride)[:, :w*4].reshape(h,w,4)
            sampled = pixels[::-1][::downsample, ::downsample]
            if code.startswith('BGR'):
                sampled = sampled[..., [2,1,0,3]]
            if byte_pixels:
                result = np.array(sampled, dtype=np.uint8, order='C', copy=True)
                if code.endswith('X'):
                    result[...,3] = 255
                return result, (w,h)
            result = np.array(sampled, dtype=np.float32, order='C', copy=True)
            result *= 1.0/255.0
            if code.endswith('X'):
                result[...,3] = 1.0
            return result, (w,h)
        finally:
            if latest is not None:
                self.lib.NDIlib_recv_free_video_v2(self.handle, C.byref(latest))

