"""Select bundled Mac dependencies for the worker's Python ABI.

Blender 4.5 uses CPython 3.11 and Blender 5.2 uses CPython 3.13. PyObjC's
native modules cannot be shared between those interpreters. Dependencies stay
inside the temporary worker directory; nothing is installed into Blender.
"""
from pathlib import Path, PurePosixPath
import platform
import sys
import zipfile


_REQUIRED = ('pyobjc_core', 'pyobjc_framework_cocoa',
             'pyobjc_framework_metal', 'syphon_python')


def _wheel_tags(path):
    """Read the standard final interpreter/ABI/platform fields of a wheel."""
    parts = path.stem.rsplit('-', 3)
    if len(parts) != 4:
        return None
    distribution = parts[0].split('-', 1)[0].lower().replace('.', '_')
    return distribution, *(set(part.split('.')) for part in parts[1:])


def select_mac_wheels(wheel_directory, python_version=None, architecture=None):
    """Return one compatible bundled wheel per required dependency.

    Optional interpreter/architecture values allow checking release packages
    without loading their native modules or importing Blender.
    """
    version = tuple(python_version or sys.version_info[:2])
    architecture = architecture or platform.machine()
    architecture = {'aarch64': 'arm64', 'AMD64': 'x86_64'}.get(architecture, architecture)
    if architecture not in {'arm64', 'x86_64'}:
        raise RuntimeError('Bundled Syphon supports Apple Silicon and Intel Macs only.')
    python_tag = 'cp' + ''.join(map(str, version))
    compatible = {name: [] for name in _REQUIRED}
    available_abis = set()
    for path in sorted(Path(wheel_directory).glob('*.whl')):
        tags = _wheel_tags(path)
        if tags is None:
            continue
        name, interpreters, abis, platforms = tags
        if name not in compatible:
            continue
        if name == 'pyobjc_core':
            available_abis.update(tag for tag in interpreters if tag.startswith('cp'))
        if not (python_tag in interpreters or ('py3' in interpreters and version[0] == 3)):
            continue
        if not abis.intersection({python_tag, 'none'}):
            continue
        if not any(tag == 'any' or (
                tag.startswith('macosx_') and tag.endswith(('_universal2', '_' + architecture)))
                for tag in platforms):
            continue
        compatible[name].append(path)
    missing = [name for name, paths in compatible.items() if not paths]
    if missing:
        supported = ', '.join('Python ' + tag[2] + '.' + tag[3:]
                              for tag in sorted(available_abis)) or 'no compatible Python ABI'
        raise RuntimeError(
            'Bundled Syphon dependencies are unavailable for Python '
            + '.'.join(map(str, version)) + ' (' + architecture + '). '
            + 'This kit includes ' + supported + '. Missing: ' + ', '.join(missing) + '.')
    duplicates = [name for name, paths in compatible.items() if len(paths) != 1]
    if duplicates:
        raise RuntimeError('Ambiguous bundled Syphon dependencies: ' + ', '.join(duplicates) + '.')
    return tuple(compatible[name][0] for name in _REQUIRED)


def extract_mac_dependencies(wheel_directory, destination, python_version=None, architecture=None):
    """Extract only this interpreter's wheels into an isolated worker folder."""
    wheels = select_mac_wheels(wheel_directory, python_version, architecture)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for wheel in wheels:
        with zipfile.ZipFile(wheel) as archive:
            for member in archive.namelist():
                path = PurePosixPath(member)
                if path.is_absolute() or '..' in path.parts:
                    raise RuntimeError('Unsafe path in bundled Syphon dependency: ' + wheel.name)
            archive.extractall(destination)
    return wheels
