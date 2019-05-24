# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

default_path = "C:\\blender\\"

bl_info = {
    "name": "Separation",
    "author": "Akim Muto",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "render > New",
    "description": "Separation",
    "warning": "",
    "wiki_url": "",
    "category": "render",
}

class Separation(bpy.types.Operator):

    bl_idname = "render.separation"               
    bl_label = "separation"   
    bl_description = "separation" 
    bl_options = {'REGISTER', 'UNDO'}
    
    temp_node_in = []
    temp_node_out = []
    
    rendering_flag = False
    
    my_path = ""
    file_type = ".png"
    
    def __remove_material_output_link(self,node_tree):
        in_node = node_tree.nodes.get("Material Output")
            
        for input in in_node.inputs:
            for input_link in input.links:
                self.temp_node_in.append([input_link.from_socket,input])
                node_tree.links.remove(input_link)
    
    def __remove_material_output_link_no_save(self,node_tree):
        in_node = node_tree.nodes.get("Material Output")
            
        for input_link in in_node.inputs[0].links:
            node_tree.links.remove(input_link)
    
    def __set_material_output(self,target,node_tree):
        in_node = node_tree.nodes.get("Material Output")
        exist_image = False

        for node in node_tree.nodes:
            if node.type == "TEX_IMAGE":
                if target in node.image.name:
                    exist_image = True
                    out_node = node
                    
                    if not node.outputs[0].links == ():
                        self.temp_node_out.append([out_node,node.outputs[0].links])
        
        if exist_image == True:
            self.rendering_flag = True    
            node_tree.links.new(out_node.outputs[0],in_node.inputs[0])
                
    def __rendering(self,file_name,context):
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            
            if context.scene.render_animation.animation_flag == True:
                bpy.context.scene.render.filepath = self.my_path + file_name + "_"
                bpy.ops.render.render(animation=True)
            else:
                bpy.ops.render.render()        
                bpy.data.images['Render Result'].save_render(filepath = self.my_path + file_name + self.file_type)

    def __recovery_link(self,node_tree):
        for node in self.temp_node_in:
             node_tree.links.new(node[0],node[1])
        
        for node in self.temp_node_out:
            for link in node[1]:
                node_tree.links.new(node[0].outputs[0],link.to_socket)    

    def execute(self, context):
        self.temp_node_in = []
        self.temp_node_out = []
        self.my_path = context.scene.separation_properties.Separation_output
        
        for material in bpy.data.materials:
            self.__remove_material_output_link(material.node_tree)
        
        for target in context.scene.custom:
            self.rendering_flag = False
            for material in bpy.data.materials:
                self.__set_material_output(target.target_string,material.node_tree)
            if  self.rendering_flag == True:
                self.__rendering(target.target_string,context)

        for material in bpy.data.materials:
            self.__remove_material_output_link_no_save(material.node_tree)
        
        for material in bpy.data.materials:
            self.__recovery_link(material.node_tree)
        
        return {'FINISHED'}             

class SeparationProperties(bpy.types.PropertyGroup):
    Separation_output = bpy.props.StringProperty(default=default_path)

class RenderAnimationProperties(bpy.types.PropertyGroup):
    animation_flag = bpy.props.BoolProperty()
    
class CUSTOM_objectCollection(bpy.types.PropertyGroup):
#    #name: StringProperty() -> Instantiated by default
    target_string: bpy.props.StringProperty()

class NewTargetString(bpy.types.PropertyGroup):
    new_target_string = bpy.props.StringProperty()

class CUSTOM_OT_actions(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.custom_index

        try:
            item = scn.custom[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.custom) - 1:
                item_next = scn.custom[idx+1].target_string
                scn.custom.move(idx, idx+1)
                scn.custom_index += 1
                info = 'Item "%s" moved to position %d' % (item.target_string, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.custom[idx-1].target_string
                scn.custom.move(idx, idx-1)
                scn.custom_index -= 1
                info = 'Item "%s" moved to position %d' % (item.target_string, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (scn.custom[idx].target_string)
                scn.custom_index -= 1
                scn.custom.remove(idx)
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            if not scn.new_target.new_target_string == "":
                item = scn.custom.add()
                item.target_string = scn.new_target.new_target_string
                scn.custom_index = len(scn.custom)-1
                info = '"%s" added to list' % (item.target_string)
                self.report({'INFO'}, info)

        return {"FINISHED"}

class OpenBrowser(bpy.types.Operator):
    bl_idname = "open.browser"
    bl_label = "open browser"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH") 

    def execute(self, context):
        context.scene.separation_properties.Separation_output = self.filepath

        return {'FINISHED'}

    def invoke(self, context, event):

        context.window_manager.fileselect_add(self) 

        return {'RUNNING_MODAL'}  

class CUSTOM_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.3)
        split.label(text="Index: %d" % (index))
        #split.prop(item, "name", text="", emboss=False, translate=False, icon=custom_icon)
        split.label(text=item.target_string, icon="HEART") # avoids renaming the item by accident

    def invoke(self, context, event):
        pass   

class SeparationPanel(bpy.types.Panel):
    """Creates a Panel in the Render properties window"""
    bl_label = "Separation"
    bl_idname = "RENDER_PT_separation"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        rows = 2
        
        row = layout.row()
        row.template_list("CUSTOM_UL_items", "", scn, "custom", scn, "custom_index", rows=rows)
        
        col = row.column(align=True)
        col.operator("custom.list_action", icon='ZOOM_OUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("custom.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("custom.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        
        col = layout.column()
        
        row = col.row(align=True)
        row.prop(scn.new_target,"new_target_string",text="target string:")
        row.operator("custom.list_action", icon='ZOOM_IN', text="").action = 'ADD'
        
        row = col.row(align=True)
        row.prop(scn.separation_properties, 'Separation_output', text='directory:')
        row.operator("open.browser", icon="FILE_FOLDER", text="")
        
        row = layout.row()
        row.prop(scn.render_animation, 'animation_flag', text='Render animation')
        
        row = layout.row()
        row.operator("render.separation")

def register():    
    bpy.utils.register_class(Separation)
    bpy.utils.register_class(SeparationProperties)
    bpy.utils.register_class(RenderAnimationProperties)
    bpy.utils.register_class(CUSTOM_objectCollection)
    bpy.utils.register_class(NewTargetString)
    bpy.utils.register_class(CUSTOM_OT_actions)
    bpy.utils.register_class(CUSTOM_UL_items)
    bpy.types.Scene.separation_properties = bpy.props.PointerProperty(type=SeparationProperties)
    bpy.types.Scene.render_animation = bpy.props.PointerProperty(type=RenderAnimationProperties)
    bpy.types.Scene.new_target = bpy.props.PointerProperty(type=NewTargetString)
    bpy.types.Scene.custom = bpy.props.CollectionProperty(type=CUSTOM_objectCollection)
    bpy.types.Scene.custom_index = bpy.props.IntProperty()
    bpy.utils.register_class(OpenBrowser)
    bpy.utils.register_class(SeparationPanel)

def unregister():
    bpy.utils.unregister_class(Separation)
    bpy.utils.unregister_class(SeparationProperties)
    bpy.utils.unregister_class(RenderAnimationProperties)
    bpy.utils.unregister_class(CUSTOM_objectCollection)
    bpy.utils.unregister_class(NewTargetString)
    bpy.utils.unregister_class(CUSTOM_OT_actions)
    bpy.utils.unregister_class(CUSTOM_UL_items)
    del bpy.types.Scene.separation_properties
    del bpy.types.Scene.render_animation
    del bpy.types.Scene.new_target
    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index
    bpy.utils.unregister_class(OpenBrowser)
    bpy.utils.unregister_class(SeparationPanel)

if __name__ == "__main__":
    register()

