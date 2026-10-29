import ctypes
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('ndi_runtime', Path(__file__).resolve().parents[1] / 'blender_video_input' / 'ndi_runtime.py')
ndi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ndi)

class DiscoveryTest(unittest.TestCase):
    def test_collapses_only_identical_endpoints_and_preserves_order(self):
        values = (ndi.Source * 5)(ndi.Source(b'one', b'url1'), ndi.Source(b'one', b'url1'), ndi.Source(b'one', b'url2'), ndi.Source(b'two', None), ndi.Source(b'two', None))
        class FakeSDK:
            def NDIlib_find_get_current_sources(self, finder, count):
                ctypes.cast(count, ctypes.POINTER(ctypes.c_uint32))[0] = len(values)
                return values
        old_sdk, old_finder = ndi._sdk, ndi._finder
        try:
            ndi._sdk, ndi._finder = FakeSDK(), 1
            self.assertEqual(ndi.discover(), [('one', 'url1'), ('one', 'url2'), ('two', '')])
        finally:
            ndi._sdk, ndi._finder = old_sdk, old_finder

if __name__ == '__main__':
    unittest.main()
