"""Isolated native capture. No bpy imports, threads, sockets, or network control.

Blender sends local JSON commands; complete frames replace a local file atomically.
Native discovery, decompression and GL/DX synchronization cannot block Blender.
"""
import ctypes as C
import json
import os
from pathlib import Path
import struct
import sys
import time
import traceback
import zipfile
import hashlib
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# The project's embedded Python deliberately omits script directories from sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

HEADER = struct.Struct('<QIIII')


def atomic(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_bytes(data)
    try:
        temp.replace(path)
        return True
    except PermissionError:
        return False  # Reader briefly has the file open on Windows; try next tick.


def parent_handle(pid):
    if os.name != 'nt':
        return None
    kernel = C.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [C.c_uint, C.c_bool, C.c_uint]
    kernel.OpenProcess.restype = C.c_void_p
    kernel.WaitForSingleObject.argtypes = [C.c_void_p, C.c_uint]
    kernel.WaitForSingleObject.restype = C.c_uint
    kernel.CloseHandle.argtypes = [C.c_void_p]
    handle = kernel.OpenProcess(0x100000, False, pid)
    if not handle:
        raise RuntimeError('The Blender parent process is unavailable.')
    return kernel, handle


def run(directory, protocol, pid):
    directory = Path(directory)
    status = {'protocol': protocol, 'status': 'Starting video worker...',
              'sources': [], 'frames': 0, 'source': '', 'last_frame': 0,
              'source_size': None, 'preview_size': None, 'closed': False}
    receiver = finder = None
    backend = None
    parent = parent_handle(pid)
    last_command_time = time.monotonic()
    last_notice = None
    previous_source = None
    next_discovery = next_retry = last_status = 0
    refresh = None
    search_until = time.monotonic() + 5
    try:
        if protocol == 'SYPHON':
            if sys.platform != 'darwin':
                raise RuntimeError('Syphon is available on macOS only.')
            if sys.version_info[:2] != (3, 13):
                raise RuntimeError('Bundled Syphon requires Blender 5.2 with Python 3.13.')
            deps = directory/'mac-deps'
            deps.mkdir(exist_ok=True)
            for wheel in sorted(Path(__file__).with_name('wheels').glob('*.whl')):
                with zipfile.ZipFile(wheel) as archive:
                    archive.extractall(deps)
            sys.path.insert(0, str(deps))
            import syphon_runtime as backend
            finder = backend.directory()
        elif protocol == 'TEST':
            import test_runtime as backend
        elif protocol == 'NDI':
            import ndi_runtime as backend
            # Resolve the installed runtime without changing system configuration.
            default = Path(os.environ.get('ProgramFiles', 'C:/Program Files'))/'NDI/NDI 6 Runtime/v6'
            if default.is_dir():
                os.environ.setdefault('NDI_RUNTIME_DIR_V6', str(default))
            backend.sdk()
        elif protocol == 'SPOUT':
            import spout_runtime as backend
            finder = backend.Library()
        else:
            raise RuntimeError('Unsupported input protocol: '+protocol)
        while True:
            if parent and parent[0].WaitForSingleObject(parent[1], 0) != 258:
                break
            try:
                cmd = json.loads((directory/'command.json').read_text(encoding='utf-8'))
            except (OSError, ValueError):
                time.sleep(.02)
                continue
            if cmd.get('stop'):
                break
            now = time.monotonic()
            if time.time()-cmd.get('heartbeat', time.time()) > 10:
                break
            if os.name != 'nt':
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    break
            if refresh != cmd.get('refresh', 0):
                refresh = cmd.get('refresh', 0)
                next_discovery = 0
                search_until = now + 5
            if now >= next_discovery:
                status['sources'] = finder.discover() if protocol == 'SPOUT' else backend.discover(0)
                next_discovery = now + (0.5 if now < search_until else 2)
            source = cmd.get('source', '') if cmd.get('connect') else ''
            if not source and cmd.get('connect') and cmd.get('auto_select'):
                sources = status['sources']
                matching = [s for s in sources if cmd.get('legacy_filter', '').lower() in s[0].lower()]
                candidates = sources
                if len(candidates) == 1:
                    source = candidates[0][0]
            if source != previous_source:
                if receiver:
                    receiver.close()
                    receiver = None
                previous_source = source
                status.update(source=source, last_frame=0, source_size=None, preview_size=None)
                next_retry = 0
            if not cmd.get('connect'):
                status['status'] = 'Disconnected - last frame retained'
            elif not source:
                status['status'] = 'Waiting for a unique source - select a source and connect'
            else:
                try:
                    if receiver is None and now >= next_retry:
                        matches = [s for s in status['sources'] if s[0] == source]
                        if matches:
                            receiver = backend.Receiver(*matches[0])
                        else:
                            status['status'] = 'Waiting for the selected source to appear'
                    if receiver:
                        downsample = int(cmd.get('downsample', 2))
                        if protocol == 'NDI':
                            frame = receiver.frame(downsample=downsample, byte_pixels=True)
                        else:
                            frame = receiver.frame(downsample=downsample, flip=cmd.get('flip', True))
                        if frame is not None:
                            pixels, size = frame
                            h, w = pixels.shape[:2]
                            seq = status['frames'] + 1
                            if atomic(directory/'latest.frame', HEADER.pack(seq,w,h,*size)+pixels.tobytes()):
                                status.update(frames=seq, last_frame=time.time(),
                                              source_size=list(size), preview_size=[w,h])
                        age = time.time() - status['last_frame'] if status['last_frame'] else float('inf')
                        status['status'] = 'Receiving frames' if age < 2 else 'Waiting for frames - start playback in the sender'
                        if age > 5 and status['last_frame']:
                            receiver.close()
                            receiver = None
                            next_retry = now + .5
                except Exception as exc:
                    notice = str(exc)
                    if notice != last_notice:
                        logging.exception('Capture failed; retrying')
                        last_notice = notice
                    status['status'] = 'Retrying: ' + str(exc)
                    if receiver:
                        receiver.close()
                        receiver = None
                    next_retry = now + 1
            status['runtime'] = getattr(backend, '_runtime_path', None)
            status['heartbeat'] = time.time()
            if now - last_status > .1:
                atomic(directory/'status.json', json.dumps(status).encode('utf-8'))
                last_status = now
            time.sleep(1 / max(1, min(30, cmd.get('fps', 15))))
    except Exception as exc:
        status['status'] = 'Video worker error: ' + str(exc)
        status['error'] = traceback.format_exc()
        logging.exception('Video worker failed')
    finally:
        try:
            if receiver:
                receiver.close()
            if protocol == 'SPOUT' and finder:
                finder.close()
            if protocol in {'NDI', 'SYPHON'} and backend:
                backend.close_finder()
        except Exception as exc:
            status['cleanup_error'] = str(exc)
        status['closed'] = True
        status['heartbeat'] = time.time()
        atomic(directory/'status.json', json.dumps(status).encode('utf-8'))
        if parent:
            parent[0].CloseHandle(parent[1])


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    run(args[0], args[1], int(args[2]))
