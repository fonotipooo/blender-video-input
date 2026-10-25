"""Binding to the bundled, SHA256-pinned SpoutLibrary DLL.

ABI: leadedge/Spout2 a26f74a11d43ef74778d73b6741d6805462702c0,
SPOUTSDK/SpoutLibrary/SpoutLibrary.h. Never load another DLL with this vtable.
All calls run in the isolated video worker, on one thread owning its GL context.
"""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path


class Library:
    def __init__(self, graphics=False):
        if os.name != 'nt':
            raise RuntimeError('Spout is available on Windows only.')
        cfg = {'sha256': 'f9cad1eb9934257f47f4219f74dd83cbb781b2b0689e9faf2a76cd7fa75a406c'}
        path = Path(__file__).parent / 'native/windows-x64/SpoutLibrary.dll'
        if not path.is_file():
            raise RuntimeError('The configured local Spout runtime is missing.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != cfg['sha256']:
            raise RuntimeError('Spout runtime changed; its native API must be checked again.')
        self.lib = C.WinDLL(str(path))
        self.lib.GetSpout.argtypes = []
        self.lib.GetSpout.restype = C.c_void_p
        self.ptr = self.lib.GetSpout()
        self.graphics = False
        if not self.ptr:
            raise RuntimeError('Could not create the Spout library.')
        self.table = C.cast(self.ptr, C.POINTER(C.POINTER(C.c_void_p))).contents
        self.call(49, None)  # Disable native log popups/console output.
        if graphics:
            if not self.call(110, C.c_bool):
                self.close()
                raise RuntimeError('Spout could not create its private OpenGL context.')
            self.graphics = True

    def call(self, index, result, args=(), values=()):
        if not self.ptr:
            raise RuntimeError('Spout library is closed.')
        return C.WINFUNCTYPE(result, C.c_void_p, *args)(self.table[index])(self.ptr, *values)

    def discover(self):
        count = self.call(74, C.c_int)
        result = []
        for index in range(min(max(0, count), 512)):
            name = C.create_string_buffer(256)
            if self.call(75, C.c_bool, (C.c_int, C.c_char_p, C.c_int), (index, name, 256)):
                result.append((name.value.decode('utf-8', errors='replace'), ''))
        return result

    def close(self):
        if self.ptr:
            try:
                self.call(15, None)
                if self.graphics:
                    self.call(111, C.c_bool)
            finally:
                self.call(119, None)
                self.ptr = None
                self.graphics = False


class Receiver:
    def __init__(self, name, url=''):
        self.sdk = Library()
        self.device = None
        self.name = name.encode('utf-8')
        self.handle = None
        self.kernel=C.WinDLL('kernel32',use_last_error=True)
        self.kernel.CreateMutexA.argtypes=[C.c_void_p,C.c_bool,C.c_char_p]
        self.kernel.CreateMutexA.restype=C.c_void_p
        self.kernel.WaitForSingleObject.argtypes=[C.c_void_p,C.c_uint]
        self.kernel.WaitForSingleObject.restype=C.c_uint
        self.kernel.ReleaseMutex.argtypes=[C.c_void_p]
        self.kernel.CloseHandle.argtypes=[C.c_void_p]
        self.mutex=self.kernel.CreateMutexA(None,False,self.name+b'_SpoutAccessMutex')
        if not self.mutex:
            self.sdk.close()
            raise RuntimeError('Could not open the Spout texture access mutex.')
        try:
            self._update_texture()
        except Exception:
            self.close()
            raise

    def _update_texture(self):
        from d3d_device import Device
        w,h,handle,fmt=C.c_uint(),C.c_uint(),C.c_void_p(),C.c_uint()
        ok=self.sdk.call(77,C.c_bool,(C.c_char_p,C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_void_p),C.POINTER(C.c_uint)),
                         (self.name,C.byref(w),C.byref(h),C.byref(handle),C.byref(fmt)))
        if not ok or not handle:
            return False
        if handle.value!=self.handle:
            if self.device:self.device.close()
            self.device=None
            self.device=Device(handle)
            self.handle=handle.value
        return True

    def frame(self, downsample=1, flip=True):
        import numpy as np
        if not self._update_texture():
            return None
        if self.kernel.WaitForSingleObject(self.mutex,0) not in (0,128):
            return None
        try:
            pixels,size=self.device.read()
        finally:
            self.kernel.ReleaseMutex(self.mutex)
        if flip:pixels=pixels[::-1]
        return np.ascontiguousarray(pixels[::downsample,::downsample]),size

    def close(self):
        self.sdk.close()
        if self.device:
            self.device.close()
            self.device=None
        if self.mutex:
            self.kernel.CloseHandle(self.mutex)
            self.mutex=None

