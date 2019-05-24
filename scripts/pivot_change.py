import bpy

bl_info = {
    "name": "pivot_change",
    "author": "Akim Muto",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "pivot > pivot: change",
    "description": "pivot change.",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Pivot"
}

addon_keymaps = []

class PivotChange(bpy.types.Operator):

    bl_idname = "pivot.pivot_change"
    bl_label = "pivot_change"
    bl_description = "Pivot change"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):        
        bpy.context.scene.tool_settings.transform_pivot_point = "MEDIAN_POINT"
        
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        op = bpy.context.active_object.matrix_world
        
        selectVerticesIndex=[]
        for i in range(len(bpy.context.active_object.data.vertices)):
            if bpy.context.active_object.data.vertices[i].select:
                selectVerticesIndex.append(i)

        mo = bpy.context.active_object.data.vertices[selectVerticesIndex[0]].co
        world_pos = op @ mo

        bpy.context.scene.cursor.location = world_pos

        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PivotChange)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    key_assign_list = []
    key_assign_list.append((PivotChange.bl_idname,"D","PRESS",False,False,False))
    if kc:
        km = kc.keymaps.new(name="3D View",space_type="VIEW_3D")
        for (idname,key,event,ctrl,alt,shift) in key_assign_list:
            kmi = km.keymap_items.new(idname,key,event,ctrl=ctrl,alt=alt,shift=shift)
            addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(PivotChange)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()