bl_info = {
    "name": "Animation Panel",
    "author": "Floo, liero",
    "version": (0,3),
    "blender": (2, 68, 0),
    "location": "Tool Shelf",
    "description": "Animation Tool in one pleace.",
    "warning": "Still work in Progress",
    "wiki_url": "",
    "tracker_url": "http://blenderartists.org/forum/showthread.php?314474-Addon-Animation-Panel-0-1",
    "category": "Animation"}


import bpy
from bpy.types import Panel, Menu
from rna_prop_ui import PropertyPanel
from bl_ui.properties_animviz import MotionPathButtonsPanel


class Animation_Panel(bpy.types.Panel):
    bl_context = "posemode"
    bl_label = "Animation Panel 0.3"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'


    def draw(self, context):
        layout = self.layout     
        
        col = layout.column(align=True)
 
        rd = context.scene.render
        am = context.active_object.data
        view = context.space_data
        scene = context.scene
        ob = context.object
        space = context.space_data
        toolsettings = context.tool_settings
        screen = context.screen
        userpref = context.user_preferences
        edit = userpref.edit 
        arm = context.object.data
        ad = context.active_object.animation_data
        interpolation = context.user_preferences.edit.keyframe_new_interpolation_type

        if ob:
            layout.template_ID(ob, "data")
        elif arm:
            layout.template_ID(space, "pin_id")               
        try:
            col = layout.column(align=True)
            col.prop(ad, "action", slider=True, text="")
        except:
            pass
        col.operator("nla.bake", text="Bake To New Action" ).bake_types={'POSE'}
        
        col = layout.column(align=True)
        row = col.row()
        row.operator("pose.paths_calculate", text="Calculate...", icon='BONE_DATA') 
        row.operator("pose.paths_update", text="Update Paths", icon='BONE_DATA')
        col.operator("pose.paths_clear", text="Delete Paths", icon='X')
        col = layout.column(align=True)
        row = col.row()
        row.operator("pose.push", text="Push")
        row.operator("pose.relax", text="Relax")
        row.operator("pose.breakdown", text="Breakdowner")    
         
        row = layout.row(align=True)
        row.prop(scene, "frame_current", text="")

        row.operator("anim.keyframe_insert_menu", text="KEY INSERT", icon='KEY_HLT')        
        
        row = layout.row(align=True)
        row.prop(toolsettings, "use_keyframe_insert_auto", text="", toggle=True)
        if toolsettings.use_keyframe_insert_auto:
            row.prop(toolsettings, "use_keyframe_insert_keyingset", text="", toggle=True)

            if screen.is_animation_playing:
                subsub = row.row()
                subsub.prop(toolsettings, "use_record_with_nla", toggle=True)   
        
        row.prop_search(scene.keying_sets_all, "active", scene, "keying_sets_all", text="")
        row.operator("screen.animation_play", text="", icon='PLAY')
        row.operator("screen.keyframe_jump", text="", icon='PREV_KEYFRAME').next = False
        row.operator("screen.keyframe_jump", text="", icon='NEXT_KEYFRAME').next = True
        
        row = layout.row(align=True)
        row.operator("anim.keyframe_clear_v3d", text="Delete Animation", icon='X_VEC')     
        row.operator("anim.keyframe_delete_v3d", text="Delete Key", icon='KEY_DEHLT')

        row = layout.row(align=True)
        row.operator("pose.loc_clear", text="Reset Loc")
        row.operator("pose.rot_clear", text="Reset Rot")
        row.operator("pose.scale_clear", text="Reset Scl")
        layout.prop(arm, "pose_position", expand=True)
        
        col = layout.column()
        col.prop(arm, "layers", text="")
        col.operator("armature.layers_show_all", text="Armature Show ALL Layers")
        
        col = layout.column(align=True)
        col.prop(edit, "keyframe_new_interpolation_type", text='Keys')
        col.prop(edit, "keyframe_new_handle_type", text="Handles")
              
        row = layout.row()
        row.prop(rd, "use_simplify", text="Simplify")
        row.prop(rd, "simplify_subdivision", text="levels")
        
        row = layout.row()
        row.prop(view, "show_only_render", text="Only Render View")
        row.prop(ob, "show_x_ray", text="X-Ray View")

        col= layout.column(align=True)
        col.label(text="Playblast:")
        
        row = layout.row(align=True)     
        row.operator("render.opengl", text="Still", icon='RENDER_STILL')
        row.operator("render.opengl", text="Animation", icon='RENDER_ANIMATION').animation = True
        row.operator("render.play_rendered_anim", text="Play", icon='PLAY')
        row = layout.row()
        row.menu("RENDER_MT_presets", text=bpy.types.RENDER_MT_presets.bl_label)
        row = layout.row(align=True)
        row.prop(scene, "use_preview_range", text="", toggle=True)
        if not scene.use_preview_range:
            row.prop(scene, "frame_start", text="Start")
            row.prop(scene, "frame_end", text="End")
        else:
            row.prop(scene, "frame_preview_start", text="Start")
            row.prop(scene, "frame_preview_end", text="End")

### delete keyframes in a range for selected bones
class DELETE_KEYFRAMES_RANGE(bpy.types.Operator):
    bl_idname = "pose.delete_keyframes"
    bl_label = "Delete Keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Delete all keyframes for selected bones in a time range"

    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return obj.type == 'ARMATURE' and obj.mode == 'POSE'

    def execute(self, context):
        wm = bpy.context.window_manager
        arm = bpy.context.object
        act = arm.animation_data.action
        delete = []

        # get selected bones names
        sel = [b.name for b in arm.data.bones if b.select]

        # get bone names from fcurve data_path
        for fcu in act.fcurves:
            name = fcu.data_path.split(sep='"', maxsplit=2)[1]

            # check if bone is selected and got keyframes in range
            if name in sel:
                for kp in fcu.keyframe_points:
                    if wm.del_range_start <= kp.co[0] <= wm.del_range_end:
                        delete.append((fcu.data_path, kp.co[0]))

        # delete keyframes
        for kp in delete:
            arm.keyframe_delete(kp[0], index=-1, frame=kp[1])

        context.scene.frame_set(context.scene.frame_current)
        return {'FINISHED'}
    
### move keyframes
drag_max = 30

def acciones(objetos):
    act = []
    for obj in objetos:
        try:
            if obj.animation_data:
                act.append(obj.animation_data.action)
            if obj.data.shape_keys and obj.data.shape_keys.animation_data:
                act.append(obj.data.shape_keys.animation_data.action)
        except:
            pass
    total = {} 
    for a in act: total[a] = 1 
    return total.keys()

def offset(act, val):
    for fcu in act.fcurves:
        if bpy.context.window_manager.sel:
            puntox = [p for p in fcu.keyframe_points if p.select_control_point]
        else:
            puntox = fcu.keyframe_points
        for k in puntox:
            k.co[0] += val
            k.handle_left[0] += val
            k.handle_right[0] += val
            
### select keys       
def drag(self, context):
    wm = context.window_manager
    if bpy.context.selected_objects:
        for act in acciones(bpy.context.selected_objects):
            offset (act, wm.drag)
    if wm.drag: wm.drag = 0
    refresco()

def refresco():
    f = bpy.context.scene.frame_current
    bpy.context.scene.frame_set(f)
    
### apply keys
class Apply(bpy.types.Operator):
    bl_idname = 'offset.apply'
    bl_label = 'Apply'
    bl_description = 'Move Keys to selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return(bpy.context.selected_objects)

    def execute(self, context):
        for act in acciones(bpy.context.selected_objects):
            offset(act, context.window_manager.off)
        refresco()
        return{'FINISHED'}
    
### reset    
class Reset(bpy.types.Operator):
    bl_idname = 'offset.reset'
    bl_label = 'Reset'
    bl_description = 'Reset sliders to zero'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.window_manager.off = 0
        return{'FINISHED'} 
###
class MOVE_KEYS(bpy.types.Panel):
    bl_label = 'Move & Delete Keys'
    bl_context = "posemode"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        layout.prop(wm,'drag',slider=True)
        column = layout.column(align=True)
        column.prop(wm,'off',slider=False)
        column.prop(wm,'sel')
        
        row = layout.row(align=True)
        row.operator('offset.reset', icon = "FILE_REFRESH")
        row.operator('offset.apply', icon = "FILE_TICK")
        col= layout.column(align=True)
        col.label(text="Delete Range Keys:") 
        
        layout = self.layout
        row = layout.row()
        row.prop(wm,'del_range_start')
        row.prop(wm,'del_range_end')
        layout.operator('pose.delete_keyframes',icon='KEY_DEHLT')

bpy.types.WindowManager.off = bpy.props.IntProperty(name='Move Keys', min=-1000, soft_min=-250, max=1000, soft_max=250, default=0, description='Offset value for f-curves in selected objects')
bpy.types.WindowManager.drag = bpy.props.IntProperty(name='Drag', min=-drag_max, max=drag_max, default=0, description='Drag to offset keyframes', update=drag)
bpy.types.WindowManager.sel = bpy.props.BoolProperty(name='Selected keys', description='Only offset Selected keyframes in selected objects')

clases = [Apply, Reset, MOVE_KEYS]

bpy.types.WindowManager.del_range_start=bpy.props.IntProperty(name='From', soft_min=0, min=-5000, soft_max=250, 
        max=5000, default=25, description='Delete keyframes range start')
bpy.types.WindowManager.del_range_end=bpy.props.IntProperty(name='To', soft_min=0, min=-5000, soft_max=250, 
        max=5000, default=75, description='Delete keyframes range end')

### ghost
class Tools_ghost(bpy.types.Panel):
    bl_context = "posemode"
    bl_label = "Ghost Object"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
     
    def draw(self, context):
        layout = self.layout
        arm = context.object.data
        layout.prop(arm, "ghost_type", expand=True)
        split = layout.split()
        col = split.column(align=True)
     
        if arm.ghost_type == 'RANGE':
            col.prop(arm, "ghost_frame_start", text="Start")
            col.prop(arm, "ghost_frame_end", text="End")
            col.prop(arm, "ghost_size", text="Step")
        elif arm.ghost_type == 'CURRENT_FRAME':
            col.prop(arm, "ghost_step", text="Range")
            col.prop(arm, "ghost_size", text="Step")
 
        col = split.column()
        col.label(text="Display:")
        col.prop(arm, "show_only_ghost_selected", text="Selected Only")

#####Uncomment if you need this#####         
#class Tools_path(bpy.types.Panel):
#    bl_context = "posemode"
#    bl_label = "Bones Motion Path"
#    bl_options = {'DEFAULT_CLOSED'}
#    bl_space_type = 'VIEW_3D'
#    bl_region_type = 'TOOLS'
#
#    def draw(self, context):
#        layout = self.layout            
#        ob = context.object
#        avs = ob.animation_visualization
#        mpath = ob.motion_path
#        MotionPathButtonsPanel.draw_settings(self, context, avs, mpath, bones=True )

### bone groups        
class Bone_group_specials(bpy.types.Menu):
    bl_label = "Bone Group Specials"
    bl_context = "posemode"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        layout = self.layout

        layout.operator("pose.group_sort", icon='SORTALPHA')

class Bone_groups(bpy.types.Panel):
    bl_label = "Bone Groups List"
    bl_context = "posemode"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.pose)

    def draw(self, context):
        layout = self.layout

        ob = context.object
        pose = ob.pose
        group = pose.bone_groups.active

        row = layout.row()

        rows = 2
        if group:
            rows = 5
        row.template_list("UI_UL_list", "bone_groups", pose, "bone_groups", pose.bone_groups, "active_index", rows=rows)

        col = row.column(align=True)
        col.active = (ob.proxy is None)
        col.operator("pose.group_add", icon='ZOOMIN', text="")
        col.operator("pose.group_remove", icon='ZOOMOUT', text="")
        col.menu("DATA_PT_bone_group_specials", icon='DOWNARROW_HLT', text="")
        if group:
            col.separator()
            col.operator("pose.group_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("pose.group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if group:
            col = layout.column()
            col.active = (ob.proxy is None)
            col.prop(group, "name")

            split = layout.split()
            split.active = (ob.proxy is None)

            col = split.column()
            col.prop(group, "color_set")
            if group.color_set:
                col = split.column()
                sub = col.row(align=True)
                sub.prop(group.colors, "normal", text="")
                sub.prop(group.colors, "select", text="")
                sub.prop(group.colors, "active", text="")

        row = layout.row()
        row.active = (ob.proxy is None)

        sub = row.row(align=True)
        sub.operator("pose.group_assign", text="Assign")
        sub.operator("pose.group_unassign", text="Remove") 
        row.operator("pose.bone_group_remove_from", text="Remove")

        sub = row.row(align=True)
        sub.operator("pose.group_select", text="Select")
        sub.operator("pose.group_deselect", text="Deselect")
        
### pose mode
class Pose_library(bpy.types.Panel):
    bl_label = "Pose Library"
    bl_context = "posemode"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.pose)

    def draw(self, context):
        layout = self.layout

        ob = context.object
        poselib = ob.pose_library

        layout.template_ID(ob, "pose_library", new="poselib.new", unlink="poselib.unlink")

        if poselib:
            # list of poses in pose library
            row = layout.row()
            row.template_list("UI_UL_list", "pose_markers", poselib, "pose_markers",
                              poselib.pose_markers, "active_index", rows=5)

            # column of operators for active pose
            # - goes beside list
            col = row.column(align=True)
            col.active = (poselib.library is None)

            # invoke should still be used for 'add', as it is needed to allow
            # add/replace options to be used properly
            col.operator("poselib.pose_add", icon='ZOOMIN', text="")

            col.operator_context = 'EXEC_DEFAULT'  # exec not invoke, so that menu doesn't need showing

            pose_marker_active = poselib.pose_markers.active

            if pose_marker_active is not None:
                col.operator("poselib.pose_remove", icon='ZOOMOUT', text="")
                col.operator("poselib.apply_pose", icon='ZOOM_SELECTED', text="").pose_index = poselib.pose_markers.active_index

            col.operator("poselib.action_sanitize", icon='HELP', text="")  # XXX: put in menu?

            # properties for active marker
            if pose_marker_active is not None:
                layout.prop(pose_marker_active, "name")
                
            col.operator("pose.copy", text="", icon="COPYDOWN")
            col.operator("pose.paste", text="", icon="PASTEDOWN")
            col.operator("pose.paste", text="", icon="PASTEFLIPUP").flipped=True

### shape key
class Shape_keys(bpy.types.Panel):
    bl_label = "Shape Keys"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        obj = context.object
        return (obj and obj.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'} and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        layout = self.layout

        ob = context.object
        key = ob.data.shape_keys
        kb = ob.active_shape_key

        enable_edit = ob.mode != 'EDIT'
        enable_edit_value = False

        if ob.show_only_shape_key is False:
            if enable_edit or (ob.type == 'MESH' and ob.use_shape_key_edit_mode):
                enable_edit_value = True

        row = layout.row()

        rows = 2
        if kb:
            rows = 5
        row.template_list("MESH_UL_shape_keys", "", key, "key_blocks", ob, "active_shape_key_index", rows=rows)

        col = row.column()

        sub = col.column(align=True)
        sub.operator("object.shape_key_add", icon='ZOOMIN', text="").from_mix = False
        sub.operator("object.shape_key_remove", icon='ZOOMOUT', text="").all = False
        sub.menu("MESH_MT_shape_key_specials", icon='DOWNARROW_HLT', text="")

        if kb:
            col.separator()

            sub = col.column(align=True)
            sub.operator("object.shape_key_move", icon='TRIA_UP', text="").type = 'UP'
            sub.operator("object.shape_key_move", icon='TRIA_DOWN', text="").type = 'DOWN'

            split = layout.split(percentage=0.4)
            row = split.row()
            row.enabled = enable_edit
            row.prop(key, "use_relative")

            row = split.row()
            row.alignment = 'RIGHT'

            sub = row.row(align=True)
            sub.label()  # XXX, for alignment only
            subsub = sub.row(align=True)
            subsub.active = enable_edit_value
            subsub.prop(ob, "show_only_shape_key", text="")
            sub.prop(ob, "use_shape_key_edit_mode", text="")

            sub = row.row()
            if key.use_relative:
                sub.operator("object.shape_key_clear", icon='X', text="")
            else:
                sub.operator("object.shape_key_retime", icon='RECOVER_LAST', text="")

            row = layout.row()
            row.prop(kb, "name")

            if key.use_relative:
                if ob.active_shape_key_index != 0:
                    row = layout.row()
                    row.active = enable_edit_value
                    row.prop(kb, "value")

                    split = layout.split()

                    col = split.column(align=True)
                    col.active = enable_edit_value
                    col.label(text="Range:")
                    col.prop(kb, "slider_min", text="Min")
                    col.prop(kb, "slider_max", text="Max")

                    col = split.column(align=True)
                    col.active = enable_edit_value
                    col.label(text="Blend:")
                    col.prop_search(kb, "vertex_group", ob, "vertex_groups", text="")
                    col.prop_search(kb, "relative_key", key, "key_blocks", text="")

            else:
                layout.prop(kb, "interpolation")
                row = layout.column()
                row.active = enable_edit_value
                row.prop(key, "eval_time")
                row.prop(key, "slurph")


def register():
    bpy.utils.register_class(Animation_Panel)
    bpy.utils.register_class(Tools_ghost)
#    bpy.utils.register_class(Tools_path)
    bpy.utils.register_class(Bone_group_specials)
    bpy.utils.register_class(Bone_groups)
    bpy.utils.register_class(Pose_library)
    bpy.utils.register_class(Shape_keys)
    bpy.utils.register_class(DELETE_KEYFRAMES_RANGE)
    for c in clases:
        bpy.utils.register_class(c)

def unregister():
    bpy.utils.unregister_class(Animation_Panel)
    bpy.utils.unregister_class(Tools_ghost)
#    bpy.utils.register_class(Tools_path)
    bpy.utils.unregister_class(Bone_group_specials)
    bpy.utils.unregister_class(Bone_groups)
    bpy.utils.unregister_class(Pose_library)
    bpy.utils.unregister_class(Shape_keys)
    bpy.utils.unregister_class(DELETE_KEYFRAMES_RANGE)
    for c in clases:
        bpy.utils.unregister_class(c)

if __name__ == "__main__": 
    register()


