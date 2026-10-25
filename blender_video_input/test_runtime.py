"""Dependency-free animated source for checking texture mapping and reception."""
import numpy as np

def discover(wait_ms=0):
    return [('Video input test pattern', '')]

class Receiver:
    def __init__(self, name, url=''):
        self.count = 0

    def frame(self, downsample=1, flip=True):
        w, h = 1280, 720
        colors = np.array([[255,255,255,255],[255,220,0,255],[0,220,230,255],
                           [0,210,70,255],[240,0,230,255],[240,30,20,255],
                           [35,50,240,255],[20,20,20,255]],dtype=np.uint8)
        xs=np.arange(0,w,downsample)
        ys=np.arange(0,h,downsample)
        pixels=np.broadcast_to(colors[np.minimum(xs*8//w,7)],(len(ys),len(xs),4)).copy()
        pixels[(ys%160)<4,:,:3]=0
        pixels[:,(xs%160)<4,:3]=0
        pixels[:,abs(xs-(self.count*20%w))<12,:3]=255
        self.count+=1
        return pixels,(w,h)

    def close(self):
        pass
