"""Minimal Windows COM lifetime for a local Spout receiver's D3D11 device.

The old DLL incorrectly stops enumerating adapters at a displayless GPU. Use
DXGI directly, and test the sender's shared texture instead of guessing a GPU.
"""
import ctypes as C
import uuid

class TextureDesc(C.Structure):
    _fields_=[(n,C.c_uint) for n in ('Width','Height','MipLevels','ArraySize','Format','SampleCount','SampleQuality','Usage','BindFlags','CPUAccessFlags','MiscFlags')]

class Mapped(C.Structure):
    _fields_=[('data',C.c_void_p),('row_pitch',C.c_uint),('depth_pitch',C.c_uint)]

def guid(value):
    return (C.c_ubyte*16).from_buffer_copy(uuid.UUID(value).bytes_le)

def method(ptr,index,result,args=()):
    table=C.cast(ptr,C.POINTER(C.POINTER(C.c_void_p))).contents
    return C.WINFUNCTYPE(result,C.c_void_p,*args)(table[index])

def release(ptr):
    if ptr:method(ptr,2,C.c_uint)(ptr)

class Device:
    def __init__(self,share_handle):
        self.device=self.context=self.texture=self.staging=None
        dxgi=C.WinDLL('dxgi');d3d=C.WinDLL('d3d11')
        create_factory=dxgi.CreateDXGIFactory1
        create_factory.argtypes=[C.c_void_p,C.POINTER(C.c_void_p)]
        create_factory.restype=C.c_int32
        create_device=d3d.D3D11CreateDevice
        create_device.argtypes=[C.c_void_p,C.c_uint,C.c_void_p,C.c_uint,C.c_void_p,C.c_uint,C.c_uint,
                               C.POINTER(C.c_void_p),C.POINTER(C.c_uint),C.POINTER(C.c_void_p)]
        create_device.restype=C.c_int32
        factory=C.c_void_p()
        if create_factory(guid('770aae78-f26f-4dba-a829-253c83d1b387'),C.byref(factory))<0:
            raise RuntimeError('Could not enumerate graphics adapters for Spout.')
        try:
            for index in range(16):
                adapter=C.c_void_p()
                hr=method(factory,12,C.c_int32,(C.c_uint,C.POINTER(C.c_void_p)))(factory,index,C.byref(adapter))
                if hr<0:break
                device=C.c_void_p();context=C.c_void_p();feature=C.c_uint()
                try:
                    hr=create_device(adapter,0,None,0x20,None,0,7,C.byref(device),C.byref(feature),C.byref(context))
                    if hr<0:continue
                    texture=C.c_void_p()
                    hr=method(device,28,C.c_int32,(C.c_void_p,C.c_void_p,C.POINTER(C.c_void_p)))(
                        device,share_handle,guid('6f15aaf2-d208-4e89-9ab4-489535d34f9c'),C.byref(texture))
                    if hr>=0:
                        self.device,self.context=device,context
                        self.texture=texture
                        self.adapter_index=index
                        device=context=None
                        return
                finally:
                    release(context);release(device);release(adapter)
        finally:
            release(factory)
        raise RuntimeError('Spout cannot open this sender texture on any local graphics adapter.')

    def read(self):
        import numpy as np
        desc=TextureDesc()
        method(self.texture,10,None,(C.POINTER(TextureDesc),))(self.texture,C.byref(desc))
        w,h=desc.Width,desc.Height
        if not w or not h or w*h>16_777_216:
            raise RuntimeError('Spout texture exceeds the local preview limit (16 megapixels).')
        if desc.Format not in (28,29,87,91):
            raise RuntimeError('Unsupported Spout texture format: '+str(desc.Format))
        if self.staging is None:
            desc.MipLevels=1;desc.ArraySize=1;desc.SampleCount=1;desc.SampleQuality=0
            desc.Usage=3;desc.BindFlags=0;desc.CPUAccessFlags=0x20000;desc.MiscFlags=0
            staging=C.c_void_p()
            hr=method(self.device,5,C.c_int32,(C.POINTER(TextureDesc),C.c_void_p,C.POINTER(C.c_void_p)))(self.device,C.byref(desc),None,C.byref(staging))
            if hr<0:raise RuntimeError('Could not allocate a Spout readback texture.')
            self.staging=staging
        method(self.context,47,None,(C.c_void_p,C.c_void_p))(self.context,self.staging,self.texture)
        mapped=Mapped()
        hr=method(self.context,14,C.c_int32,(C.c_void_p,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Mapped)))(
            self.context,self.staging,0,1,0,C.byref(mapped))
        if hr<0:raise RuntimeError('Spout texture readback failed.')
        try:
            raw=np.ctypeslib.as_array(C.cast(mapped.data,C.POINTER(C.c_ubyte)),shape=(mapped.row_pitch*h,))
            pixels=raw.reshape(h,mapped.row_pitch)[:,:w*4].reshape(h,w,4).copy()
            if desc.Format in (87,91):pixels=pixels[...,[2,1,0,3]]
            return pixels,(w,h)
        finally:
            method(self.context,15,None,(C.c_void_p,C.c_uint))(self.context,self.staging,0)

    def close(self):
        release(self.staging);release(self.texture)
        release(self.context);release(self.device)
        self.context=self.device=self.texture=self.staging=None
