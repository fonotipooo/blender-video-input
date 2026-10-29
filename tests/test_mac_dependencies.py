"""Checks that both supported Blender Python ABIs remain isolated."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('mac_dependencies', ROOT / 'blender_video_input/mac_dependencies.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
WHEELS = ROOT / 'blender_video_input/wheels'


class MacDependenciesTest(unittest.TestCase):
    def test_each_supported_abi_selects_only_its_native_wheels(self):
        for version in ((3, 11), (3, 13)):
            for architecture in ('arm64', 'x86_64'):
                with self.subTest(version=version, architecture=architecture):
                    wheels = MODULE.select_mac_wheels(WHEELS, version, architecture)
                    self.assertEqual(len(wheels), 4)
                    native = [path.name for path in wheels if path.name.startswith('pyobjc')]
                    tag = 'cp' + ''.join(map(str, version))
                    self.assertEqual(len(native), 3)
                    self.assertTrue(all('-' + tag + '-' + tag + '-' in name for name in native))
                    self.assertTrue(any(path.name.startswith('syphon_python-0.2.0-py3-none-') for path in wheels))

    def test_unsupported_python_fails_before_extracting(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / 'deps'
            with self.assertRaisesRegex(RuntimeError, r'Python 3\.12.*Python 3\.11.*Python 3\.13'):
                MODULE.extract_mac_dependencies(WHEELS, destination, (3, 12), 'arm64')
            self.assertFalse(destination.exists())

    def test_extraction_contains_no_other_interpreter_modules(self):
        for version in ((3, 11), (3, 13)):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as folder:
                destination = Path(folder) / 'deps'
                MODULE.extract_mac_dependencies(WHEELS, destination, version, 'arm64')
                extensions = list(destination.rglob('*.so'))
                self.assertTrue(extensions)
                expected = 'cpython-' + ''.join(map(str, version))
                self.assertTrue(all(expected in path.name for path in extensions))
                self.assertTrue((destination / 'syphon/libs/Syphon.framework/Syphon').is_file())

    def test_missing_dependency_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(RuntimeError, 'Missing: pyobjc_core'):
                MODULE.select_mac_wheels(folder, (3, 11), 'arm64')

    def test_unsafe_archive_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            wheels = root / 'wheels'
            wheels.mkdir()
            for name in MODULE._REQUIRED:
                tags = 'py3-none' if name == 'syphon_python' else 'cp311-cp311'
                with zipfile.ZipFile(wheels / (name + '-1.0-' + tags + '-macosx_12_0_universal2.whl'), 'w') as archive:
                    archive.writestr('../escaped', 'unexpected')
            with self.assertRaisesRegex(RuntimeError, 'Unsafe path'):
                MODULE.extract_mac_dependencies(wheels, root / 'deps', (3, 11), 'arm64')
            self.assertFalse((root / 'escaped').exists())


if __name__ == '__main__':
    unittest.main()
