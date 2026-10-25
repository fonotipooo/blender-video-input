bl_info = {
    'name': 'Live Video Input', 'author': 'Contributors',
    'version': (0, 3, 0), 'blender': (5, 2, 0),
    'location': '3D View > Sidebar > Video Input',
    'description': 'Apply live Spout, Syphon, NDI or local video textures to selected objects',
    'category': 'Material',
}
import sys
import platform
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import atexit
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import textwrap
import time
import zlib
import bpy
from bpy.app.handlers import persistent

_state = dict(process=None, directory=None, log=None, scene=None, mode='idle',
              worker_protocol=None, stopping=0, frames=0, last_frame=0,
              source_size=None, preview_size=None, source='', seq=0, refresh=0,
              last_command=None, last_worker_status={}, forced_stops=0)
_sources = []
_enum_cache = [('NONE','No source selected','Refresh to find available sources',0)]
_HEADER = struct.Struct('<QIIII')

def _target_node(scene=None):
    scene=scene or _state.get('scene') or bpy.context.scene
    material=scene.bvi_video_target_material
    if not material or not material.use_nodes:
        raise RuntimeError('Select a mesh and click Apply to selected objects first.')
    node=material.node_tree.nodes.get(scene.bvi_video_target_node)
    if not node or node.bl_idname!='ShaderNodeTexImage':
        raise RuntimeError('The selected material needs a valid Image Texture destination node.')
    return node

def _publish(pixels, source_size):
    node = _target_node()
    height,width = pixels.shape[:2]
    image = bpy.data.images.get('BVI_LIVE_PREVIEW')
    if image is None:
        old = node.image
        image = bpy.data.images.new('BVI_LIVE_PREVIEW',width,height,alpha=True,float_buffer=False)
        if old:
            image.colorspace_settings.name = old.colorspace_settings.name
    elif tuple(image.size) != (width,height):
        image.scale(width,height)
    if node.image != image:
        node.image = image
    image.pixels.foreach_set(pixels.ravel())
    image.update()
    # Refresh the GPU image after CPU pixels change (Blender Windows live preview).
    if hasattr(image, 'gl_free'):
        image.gl_free()
    image.update_tag()
    _state.update(source_size=list(source_size),preview_size=[width,height],
                  frames=_state['frames']+1,last_frame=time.monotonic())

def _selected(scene):
    return {'NDI': scene.bvi_video_ndi_selected, 'SPOUT': scene.bvi_video_spout_selected, 'SYPHON': scene.bvi_video_syphon_selected, 'TEST': 'Video input test pattern'}.get(scene.bvi_video_protocol, '')

def _set_selected(scene,name):
    if scene.bvi_video_protocol=='NDI':
        scene.bvi_video_ndi_selected=name
    elif scene.bvi_video_protocol=='SPOUT':
        scene.bvi_video_spout_selected=name
    elif scene.bvi_video_protocol=='SYPHON':
        scene.bvi_video_syphon_selected=name

def _source_items(self,context):
    return _enum_cache

def _source_get(scene):
    return next((v[3] for v in _enum_cache if v[0]==_selected(scene)),0)

def _source_set(scene,value):
    for identifier,label,description,number in _enum_cache:
        if number==value:
            _set_selected(scene,'' if identifier=='NONE' else identifier)
            _state.update(source_size=None,preview_size=None,source='',last_frame=0)
            break

def _update_sources(scene,values):
    global _sources,_enum_cache
    _sources=list(values)
    names=[s[0] for s in values]
    selected=_selected(scene)
    if selected and selected not in names:
        names.append(selected)
    items=[('NONE','No source selected','Choose a source or refresh discovery',0)]
    used={0}
    for name in names:
        number=zlib.crc32(name.encode('utf-8')) & 0x7fffffff
        while number in used:
            number=(number+1) & 0x7fffffff
        used.add(number)
        label=name if any(s[0]==name for s in values) else name+' (not currently listed)'
        items.append((name,label,name,number))
    _enum_cache=items  # Retain strings for Blender's dynamic enum lifetime.

def _command(scene):
    return dict(connect=_state['mode']=='connect',source=_selected(scene),
                auto_select=not bool(_selected(scene)),legacy_filter=scene.bvi_capture_source,
                downsample=int(scene.bvi_capture_downsample),fps=scene.bvi_capture_fps,
                flip=scene.bvi_video_flip,refresh=_state['refresh'])

def _write_command(command):
    command['heartbeat']=time.time()
    directory=_state['directory']
    if directory and command!=_state['last_command']:
        temp=directory/'command.tmp'
        temp.write_text(json.dumps(command),encoding='utf-8')
        try:
            temp.replace(directory/'command.json')
            _state['last_command']=command
        except PermissionError:
            pass

def _ensure_timer():
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick,first_interval=.05)

def _request_close():
    if _state['process'] and not _state['stopping']:
        _write_command({'stop':True})
        _state['stopping']=time.monotonic()

def _clean_worker():
    directory=_state['directory']
    if directory:
        try:
            _state['last_worker_status']=json.loads((directory/'status.json').read_text())
        except (OSError,ValueError):
            pass
    if directory:
        try:
            content=(directory/'worker.log').read_text(encoding='utf-8', errors='replace')
            if content.strip():
                _logger().info('Worker output:\n%s', content[-60000:])
        except OSError:
            pass
    if _state['log']:
        _state['log'].close()
    if directory and directory.name.startswith('bvi-video-') and directory.parent==Path(tempfile.gettempdir()):
        shutil.rmtree(directory,ignore_errors=True)
    _state.update(process=None,directory=None,log=None,worker_protocol=None,
                  stopping=0,last_command=None,seq=0)

def _spawn(scene):
    protocol=scene.bvi_video_protocol
    if protocol=='SYPHON' and sys.platform!='darwin':
        raise RuntimeError('Syphon requires macOS. Choose NDI on this computer.')
    if protocol=='SPOUT' and os.name!='nt':
        raise RuntimeError('Spout requires Windows. Choose NDI on this computer.')
    directory=Path(tempfile.mkdtemp(prefix='bvi-video-'))
    # Copy resources into a path visible to child processes, including Store Blender.
    source=Path(__file__).resolve().parent
    for module in source.glob('*.py'):
        if module.name!='__init__.py':
            shutil.copy2(module,directory/module.name)
    if protocol=='SPOUT':
        shutil.copytree(source/'native',directory/'native')
    if protocol=='SYPHON':
        shutil.copytree(source/'wheels',directory/'wheels')
    worker=directory/'video_worker.py'
    bindir=Path(sys.prefix)/'bin'
    executables=([bindir/'python.exe'] if os.name=='nt' else sorted(bindir.glob('python3.*')))
    executable=next((p for p in executables if p.is_file() and not p.name.endswith('-config')),None)
    if executable:
        args=[str(executable),'-B',str(worker),str(directory),protocol,str(os.getpid())]
    else:
        args=[bpy.app.binary_path,'--background','--factory-startup','--disable-autoexec','--python',str(worker),'--',str(directory),protocol,str(os.getpid())]
    environment=os.environ.copy()
    if scene.bvi_video_ndi_runtime:
        environment['BVI_NDI_RUNTIME']=bpy.path.abspath(scene.bvi_video_ndi_runtime)
    _state.update(directory=directory,last_command=None,seq=0,frames=0,
                  last_frame=0,source_size=None,preview_size=None,source='',last_worker_status={})
    _write_command(_command(scene))
    log=(directory/'worker.log').open('w',encoding='utf-8')
    try:
        process=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,env=environment,
                                 creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    except Exception:
        log.close()
        _clean_worker()
        raise RuntimeError('Could not start the local video worker.')
    _state.update(process=process,log=log,worker_protocol=protocol)
    _logger().info('Starting %s worker', protocol)
    scene.bvi_capture_status='Starting '+('Spout' if protocol=='SPOUT' else protocol)+' worker...'

def start(scene,timer=True):
    _target_node(scene)
    if scene.bvi_video_protocol=='FILE':
        path=bpy.path.abspath(scene.bvi_video_file)
        if not Path(path).is_file():
            raise RuntimeError('Choose an image or movie file first.')
        image=bpy.data.images.load(path, check_existing=True)
        node=_target_node()
        node.image=image
        if image.source=='MOVIE':
            node.image_user.use_auto_refresh=True
            node.image_user.frame_duration=image.frame_duration
            node.image_user.use_cyclic=True
            scene.frame_end=max(scene.frame_end,image.frame_duration)
        _state.update(scene=scene,mode='local',source_size=list(image.size),preview_size=list(image.size),source=Path(path).name)
        scene.bvi_capture_running=True
        scene.bvi_capture_status='Local movie ready - play the timeline' if image.source=='MOVIE' else 'Local image loaded'
        _logger().info('Local media loaded: %s', Path(path).name)
        _redraw()
        return
    _state.update(scene=scene,mode='connect')
    scene.bvi_capture_running=True
    scene.bvi_capture_status='Connecting - waiting for actual frames'
    if timer:
        _ensure_timer()

def stop():
    scene=_state['scene']
    _state['mode']='idle'
    _request_close()
    if scene and hasattr(scene,'bvi_capture_running'):
        scene.bvi_capture_running=False
        scene.bvi_capture_status='Disconnecting...' if _state['process'] else 'Disconnected - last frame retained'
    _state.update(source_size=None,preview_size=None,source='',last_frame=0)
    if _state['process']:
        _ensure_timer()

def _protocol_changed(scene,context):
    connecting=_state['mode'] in {'connect','local'}
    _request_close()
    _state.update(scene=scene,mode='connect' if connecting else 'discover',
                  source_size=None,preview_size=None,source='',last_frame=0)
    _update_sources(scene,[])
    scene.bvi_capture_running=connecting
    scene.bvi_capture_status='Releasing the previous connection...'
    _ensure_timer()

def _redraw():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type in {'VIEW_3D','IMAGE_EDITOR'}:
                area.tag_redraw()

def _tick():
    scene=_state['scene']
    try:
        process=_state['process']
        if process:
            if process.poll() is not None:
                expected=bool(_state['stopping'])
                code=process.returncode
                _clean_worker()
                if not expected:
                    _state['mode']='idle'
                    if scene:
                        scene.bvi_capture_running=False
                        detail=_state['last_worker_status'].get('status','Native worker exited with code '+str(code))
                        scene.bvi_capture_status=detail+' - press Connect to retry'
            elif _state['stopping']:
                if time.monotonic()-_state['stopping']>2:
                    process.kill()  # Only our Popen child, never another application.
                    _state['forced_stops']+=1
                return .05
            elif scene and _state['worker_protocol']!=scene.bvi_video_protocol:
                _request_close()
                return .05
        if scene and scene.bvi_video_protocol=='FILE':
            if _state['mode']=='connect':
                start(scene)
            return None
        if not scene or _state['mode'] in {'idle','local'}:
            if scene and scene.bvi_capture_status=='Disconnecting...':
                scene.bvi_capture_status='Disconnected - last frame retained'
            _redraw()
            return None
        if _state['process'] is None:
            _spawn(scene)
            if _state['mode']=='idle':
                _redraw()
                return None
        _write_command(_command(scene))
        directory=_state['directory']
        try:
            status=json.loads((directory/'status.json').read_text(encoding='utf-8'))
        except (OSError,ValueError):
            return .05
        _update_sources(scene,status.get('sources',[]))
        name=status.get('source','')
        if name and not _selected(scene):
            _set_selected(scene,name)
            _update_sources(scene,status.get('sources',[]))
        scene.bvi_capture_status=status.get('status','Waiting for worker')
        if status.get('error') and status.get('error')!=_state.get('last_error'):
            _logger().error('%s',status['error'])
            _state['last_error']=status['error']
        age=time.time()-status.get('last_frame',0)
        heartbeat_age=time.time()-status.get('heartbeat',0)
        if heartbeat_age>3:
            scene.bvi_capture_status='Video worker is not responding - disconnect to release it'
        elif (_state['mode']=='connect' and name==_selected(scene) and age<2
              and status.get('frames',0)!=_state['seq']):
            import numpy as np
            try:
                data=(directory/'latest.frame').read_bytes()
            except (FileNotFoundError,PermissionError):
                return .05
            seq,w,h,sw,sh=_HEADER.unpack_from(data)
            if w*h>16_777_216:
                raise RuntimeError('Preview exceeds 16 megapixels. Choose Half or Quarter in Advanced settings.')
            if seq==status['frames'] and len(data)==_HEADER.size+w*h*4:
                pixels=np.frombuffer(data,dtype=np.uint8,offset=_HEADER.size).reshape(h,w,4).astype(np.float32)
                pixels*=1/255
                _publish(pixels,(sw,sh))
                _state.update(seq=seq,source=name)
                protocol={'SPOUT':'Spout','SYPHON':'Syphon','NDI':'NDI','TEST':'Test pattern'}[scene.bvi_video_protocol]
                scene.bvi_capture_status='Live - '+protocol+' frames received'
        elif age>=2 and _state['mode']=='connect':
            _state.update(source_size=None,preview_size=None)
        _redraw()
        return 1/max(1,scene.bvi_capture_fps)
    except Exception as exc:
        _logger().exception('Video input error')
        _state['mode']='idle'
        _request_close()
        if scene:
            scene.bvi_capture_running=False
            scene.bvi_capture_status='Video input error: '+str(exc)
        return .05 if _state['process'] else None

class BVI_OT_video_apply(bpy.types.Operator):
    bl_idname='bvi.video_apply'
    bl_label='Apply to selected objects'
    bl_description='Create a video material and assign it to the selected mesh objects'
    bl_options={'REGISTER','UNDO'}

    @classmethod
    def poll(cls,context):
        return context.mode=='OBJECT' and any(obj.type=='MESH' for obj in context.selected_objects)

    def execute(self,context):
        scene=context.scene
        material=scene.bvi_video_target_material
        if material is None:
            material=bpy.data.materials.new('Live Video Input')
            material.use_nodes=True
            tree=material.node_tree
            tree.nodes.clear()
            image=tree.nodes.new('ShaderNodeTexImage')
            image.name='Live Video Input'
            image.label='Video input'
            image.location=(-400,0)
            emission=tree.nodes.new('ShaderNodeEmission')
            emission.location=(-100,0)
            output=tree.nodes.new('ShaderNodeOutputMaterial')
            output.location=(150,0)
            tree.links.new(image.outputs['Color'],emission.inputs['Color'])
            tree.links.new(emission.outputs['Emission'],output.inputs['Surface'])
            scene.bvi_video_target_material=material
            scene.bvi_video_target_node=image.name
        try:
            _target_node(scene)
        except Exception as exc:
            self.report({'ERROR'},str(exc))
            return {'CANCELLED'}
        for obj in context.selected_objects:
            if obj.type!='MESH':
                continue
            if obj.data.users>1:
                obj.data=obj.data.copy()
            slots=obj.data.materials
            index=next((i for i,slot in enumerate(slots) if slot==material),None)
            if index is None:
                slots.append(material)
                index=len(slots)-1
            for face in obj.data.polygons:
                face.material_index=index
            obj.active_material_index=index
        self.report({'INFO'},'Video material applied. Choose an input and connect.')
        _logger().info('Video material applied to selected mesh objects')
        return {'FINISHED'}

class BVI_OT_video_refresh(bpy.types.Operator):
    bl_idname='bvi.video_refresh'
    bl_label='Refresh'
    bl_description='Discover sources without blocking Blender'
    def execute(self,context):
        _state['scene']=context.scene
        _state['refresh']+=1
        if _state['mode']!='connect':
            _state['mode']='discover'
        _ensure_timer()
        return {'FINISHED'}

class BVI_OT_video_connect(bpy.types.Operator):
    bl_idname='bvi.video_connect'
    bl_label='Connect'
    def execute(self,context):
        try:
            start(context.scene)
            return {'FINISHED'}
        except Exception as exc:
            _logger().exception('Connect failed')
            context.scene.bvi_capture_status=str(exc)
            self.report({'ERROR'},str(exc))
            return {'CANCELLED'}

class BVI_OT_video_disconnect(bpy.types.Operator):
    bl_idname='bvi.video_disconnect'
    bl_label='Disconnect'
    def execute(self,context):
        stop()
        return {'FINISHED'}

class BVI_PT_video(bpy.types.Panel):
    bl_label='Live Video Input'
    bl_idname='BVI_PT_video'
    bl_space_type='VIEW_3D'
    bl_region_type='UI'
    bl_category='Video Input'
    def draw(self,context):
        layout,scene=self.layout,context.scene
        width=max(24,int(context.region.width/7))
        layout.operator('bvi.video_apply',icon='MATERIAL')
        if scene.bvi_video_target_material:
            layout.label(text='Destination: '+scene.bvi_video_target_material.name)
        layout.prop(scene,'bvi_video_protocol',text='Input')
        if scene.bvi_video_protocol=='FILE':
            layout.prop(scene,'bvi_video_file',text='File')
        else:
            row=layout.row(align=True)
            row.prop(scene,'bvi_video_source',text='Source')
            row.operator('bvi.video_refresh',text='',icon='FILE_REFRESH')
            layout.label(text=f'Available sources: {len(_sources)}')
        if scene.bvi_video_protocol=='NDI':
            layout.operator('wm.url_open',text='NDI runtime and information',icon='URL').url='https://ndi.video/'
            for line in textwrap.wrap('NDI® is a registered trademark of Vizrt NDI AB',width=width):
                layout.label(text=line)
        if scene.bvi_video_protocol=='SYPHON':
            for line in textwrap.wrap('Mac receiver: experimental; hardware testing pending',width=width):
                layout.label(text=line,icon='INFO' if line.startswith('Mac') else 'NONE')
        row=layout.row(align=True)
        row.operator('bvi.video_connect',text='Load' if scene.bvi_video_protocol=='FILE' else 'Connect',icon='LINKED')
        row.operator('bvi.video_disconnect',icon='UNLINKED')
        box=layout.box()
        box.label(text='Status')
        for line in textwrap.wrap(scene.bvi_capture_status,width=width):
            box.label(text=line)
        size,preview=_state['source_size'],_state['preview_size']
        box.label(text=f'Received: {size[0]} x {size[1]}' if size else 'Received: no current frames')
        if preview:
            box.label(text=f'Preview: {preview[0]} x {preview[1]}')
        row=layout.row()
        row.prop(scene,'bvi_video_advanced',text='Advanced and troubleshooting',icon='TRIA_DOWN' if scene.bvi_video_advanced else 'TRIA_RIGHT',emboss=False)
        if scene.bvi_video_advanced:
            col=layout.column()
            col.prop(scene,'bvi_video_target_material',text='Material')
            col.prop(scene,'bvi_video_target_node',text='Texture node')
            col.prop(scene,'bvi_capture_downsample',text='Preview quality')
            col.prop(scene,'bvi_capture_fps',text='Maximum FPS')
            if scene.bvi_video_protocol in {'SPOUT','SYPHON'}:
                col.prop(scene,'bvi_video_flip',text='Flip vertically')
            col.prop(scene,'bvi_capture_autoconnect',text='Auto-connect on file open')
            if scene.bvi_video_protocol=='NDI':
                col.prop(scene,'bvi_video_ndi_runtime',text='NDI library')
                col.label(text='Disconnect and reconnect after changing it')
            col.operator('bvi.video_view_log',icon='TEXT')
            col.operator('bvi.video_export_log',icon='EXPORT')
            col.label(text='Live Video Input 0.3.0 beta')


@persistent
def _before_load(_):
    stop()
    _state['scene']=None

def _auto_start():
    scene=bpy.context.scene
    if scene and scene.bvi_capture_autoconnect:
        try:
            start(scene)
        except Exception as exc:
            scene.bvi_capture_status=str(exc)
    return None

@persistent
def _after_load(_):
    if not bpy.app.timers.is_registered(_auto_start):
        bpy.app.timers.register(_auto_start,first_interval=1)

def _exit_cleanup():
    process=_state.get('process')
    if process and process.poll() is None:
        try:
            _write_command({'stop':True})
            try:
                process.wait(timeout=.7)
            except subprocess.TimeoutExpired:
                process.terminate()
        except OSError:
            pass

def _log_path():
    folder=Path(bpy.utils.user_resource('CONFIG'))/'blender_video_input'
    folder.mkdir(parents=True,exist_ok=True)
    return folder/'video-input.log'

_log_instance=None
def _logger():
    global _log_instance
    if _log_instance is None:
        _log_instance=logging.getLogger(__name__)
        _log_instance.setLevel(logging.INFO)
        handler=RotatingFileHandler(_log_path(),maxBytes=1_000_000,backupCount=2,encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        _log_instance.addHandler(handler)
        _log_instance.propagate=False
    return _log_instance

def _diagnostic_text(scene):
    text='Live Video Input 0.3.0 beta\n'+json.dumps(dict(blender=bpy.app.version_string,python=platform.python_version(),system=platform.system(),architecture=platform.machine(),protocol=scene.bvi_video_protocol,status=scene.bvi_capture_status,source=_selected(scene),received=_state['source_size'],preview=_state['preview_size'],frames=_state['frames'],worker_status=_state['last_worker_status']),indent=2)+'\n\n'
    paths=[_log_path()]
    if _state['directory']:
        paths += [_state['directory']/'worker.log',_state['directory']/'status.json']
    for path in paths:
        if path.is_file():
            text+='\n--- '+path.name+' ---\n'+path.read_text(encoding='utf-8',errors='replace')[-100000:]
    # Reports stay local; mask home paths before users choose to share them.
    home=str(Path.home())
    text=text.replace(json.dumps(home)[1:-1],'<home>').replace(home,'<home>').replace(home.replace('\\','/'),'<home>')
    return text

class BVI_OT_video_view_log(bpy.types.Operator):
    bl_idname='bvi.video_view_log'
    bl_label='Show error log'
    def execute(self,context):
        block=bpy.data.texts.get('Live Video Support Log') or bpy.data.texts.new('Live Video Support Log')
        block.clear()
        block.write(_diagnostic_text(context.scene))
        if context.area:
            context.area.type='TEXT_EDITOR'
            context.area.spaces.active.text=block
        return {'FINISHED'}

class BVI_OT_video_export_log(bpy.types.Operator):
    bl_idname='bvi.video_export_log'
    bl_label='Export support log'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_glob: bpy.props.StringProperty(default='*.txt',options={'HIDDEN'})
    def invoke(self,context,event):
        self.filepath='video-input-support-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.txt'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    def execute(self,context):
        try:
            Path(self.filepath).write_text(_diagnostic_text(context.scene),encoding='utf-8')
            self.report({'INFO'},'Support log saved. Review source names before sharing.')
            return {'FINISHED'}
        except OSError as exc:
            self.report({'ERROR'},str(exc))
            return {'CANCELLED'}

_classes=(BVI_OT_video_apply,BVI_OT_video_refresh,BVI_OT_video_connect,BVI_OT_video_disconnect,BVI_OT_video_view_log,BVI_OT_video_export_log,BVI_PT_video)
_properties=('bvi_video_target_material','bvi_video_target_node','bvi_capture_source','bvi_capture_downsample','bvi_capture_fps',
             'bvi_capture_autoconnect','bvi_capture_running','bvi_capture_status',
             'bvi_video_protocol','bvi_video_source','bvi_video_ndi_selected','bvi_video_spout_selected','bvi_video_syphon_selected','bvi_video_flip','bvi_video_file','bvi_video_advanced','bvi_video_ndi_runtime')

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    S=bpy.types.Scene
    S.bvi_video_target_material=bpy.props.PointerProperty(type=bpy.types.Material)
    S.bvi_video_target_node=bpy.props.StringProperty(default='Live Video Input')
    S.bvi_video_ndi_selected=bpy.props.StringProperty(default='')
    S.bvi_video_spout_selected=bpy.props.StringProperty(default='')
    S.bvi_video_syphon_selected=bpy.props.StringProperty(default='')
    items=[('TEST','Test pattern','Check the texture input without another app'),('FILE','Image or video file','Load local media; play the timeline for movies')]
    if os.name=='nt':
        items.append(('SPOUT','Spout (Windows)','Receive video from another app on this PC'))
    if sys.platform=='darwin':
        items.append(('SYPHON','Syphon (Mac, experimental)','Receive a local Syphon sender; Mac hardware validation pending'))
    items.append(('NDI','NDI®','Receive local or network video; requires the official NDI runtime'))
    S.bvi_video_protocol=bpy.props.EnumProperty(name='Input',items=items,default='TEST',update=_protocol_changed)
    S.bvi_video_source=bpy.props.EnumProperty(name='Source',items=_source_items,get=_source_get,set=_source_set)
    S.bvi_video_flip=bpy.props.BoolProperty(default=True)
    S.bvi_video_file=bpy.props.StringProperty(subtype='FILE_PATH')
    S.bvi_video_ndi_runtime=bpy.props.StringProperty(subtype='FILE_PATH')
    S.bvi_video_advanced=bpy.props.BoolProperty(default=False)
    S.bvi_capture_source=bpy.props.StringProperty(default='')
    S.bvi_capture_downsample=bpy.props.EnumProperty(items=[('1','Full','Full received image'),('2','Half','Half width and height'),('4','Quarter','Quarter width and height')],default='2')
    S.bvi_capture_fps=bpy.props.IntProperty(default=15,min=1,max=30)
    S.bvi_capture_autoconnect=bpy.props.BoolProperty(default=False)
    S.bvi_capture_running=bpy.props.BoolProperty(default=False,options={'SKIP_SAVE'})
    S.bvi_capture_status=bpy.props.StringProperty(default='Choose Test pattern and press Connect to begin',options={'SKIP_SAVE'})
    bpy.app.handlers.load_pre.append(_before_load)
    bpy.app.handlers.load_post.append(_after_load)
    atexit.register(_exit_cleanup)
    _logger().info('Registered on Blender %s, %s %s',bpy.app.version_string,platform.system(),platform.machine())

def unregister():
    global _log_instance
    _exit_cleanup()
    process=_state.get('process')
    if process:
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)
        _clean_worker()
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    if bpy.app.timers.is_registered(_auto_start):
        bpy.app.timers.unregister(_auto_start)
    _state.update(scene=None,mode='idle')
    for handlers,callback in [(bpy.app.handlers.load_pre,_before_load),(bpy.app.handlers.load_post,_after_load)]:
        if callback in handlers:
            handlers.remove(callback)
    atexit.unregister(_exit_cleanup)
    for name in reversed(_properties):
        if hasattr(bpy.types.Scene,name):
            delattr(bpy.types.Scene,name)
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
    if _log_instance:
        for handler in list(_log_instance.handlers):
            handler.close()
            _log_instance.removeHandler(handler)
        _log_instance=None
