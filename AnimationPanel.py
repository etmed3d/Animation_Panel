bl_info = {
    "name": "Animation Panel",
    "author": "Daniel Banasik",
    "version": (0,1),
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
    bl_label = "Animation Panel"
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

        if ob:
            layout.template_ID(ob, "data")
        elif arm:
            layout.template_ID(space, "pin_id")               

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

        row.operator("screen.keyframe_jump", text="", icon='PREV_KEYFRAME').next = False
        row.operator("screen.keyframe_jump", text="", icon='NEXT_KEYFRAME').next = True
        row = layout.row(align=True)
        row.operator("anim.keyframe_clear_v3d", text="Delete Animation", icon='X_VEC')     
        row.operator("anim.keyframe_delete_v3d", text="Delete Key", icon='KEY_DEHLT')

        col = layout.column(align=True)
        col.operator("nla.bake", text="Bake To New Action" ).bake_types={'POSE'}
       
        row = layout.row(align=True)
        row.operator("pose.loc_clear", text="Reset Loc")
        row.operator("pose.rot_clear", text="Reset Rot")
        row.operator("pose.scale_clear", text="Reset Scl") 
      
        col = layout.column()
        col.prop(view, "show_only_render", text="Only Render View")
        col.prop(ob, "show_x_ray", text="X-Ray View")

        col= layout.column(align=True)
        col.label(text="Playblast:")
        row = layout.row(align=True)     
        row.operator("render.opengl", text="Still", icon='RENDER_STILL')
        row.operator("render.opengl", text="Animation", icon='RENDER_ANIMATION').animation = True
        row.operator("render.play_rendered_anim", text="Play", icon='PLAY')

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

def register():
    bpy.utils.register_class(Animation_Panel)
    bpy.utils.register_class(Tools_ghost)
#    bpy.utils.register_class(Tools_path)
    bpy.utils.register_class(Bone_group_specials)
    bpy.utils.register_class(Bone_groups)
    bpy.utils.register_class(Pose_library)

def unregister():
    bpy.utils.unregister_class(Animation_Panel)
    bpy.utils.unregister_class(Tools_ghost)
#    bpy.utils.register_class(Tools_path)
    bpy.utils.unregister_class(Bone_group_specials)
    bpy.utils.unregister_class(Bone_groups)
    bpy.utils.unregister_class(Pose_library)


if __name__ == "__main__": 
    register()
