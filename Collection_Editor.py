bl_info = {
    "name": "Collection Editor By BHiMAX",
    "blender": (2, 80, 0),
    "category": "BHiMAX",
    "author": "Bhimraj Malviya",
    "description": "Create collections and manage objects with visibility control.",
    "version": (2, 1, 0),
}

import bpy

class BHiMAX_ObjectProperty(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)

class BHiMAX_Collection(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    is_selected: bpy.props.BoolProperty(default=False)
    hide_viewport: bpy.props.BoolProperty(name="Viewport Visibility", default=False)
    hide_render: bpy.props.BoolProperty(name="Render Visibility", default=False)
    objects: bpy.props.CollectionProperty(type=BHiMAX_ObjectProperty)

class BHiMAX_CollectionCreatorOperator(bpy.types.Operator):
    bl_idname = "bhimax.new_collection"
    bl_label = "New Collection"
    
    def execute(self, context):
        # Create a new collection
        new_collection = context.scene.bhimax_collections.add()
        new_collection.name = "Collection"
        return {'FINISHED'}

class BHiMAX_RemoveCollectionOperator(bpy.types.Operator):
    bl_idname = "bhimax.remove_collection"
    bl_label = "Remove Collection"
    
    collection_index: bpy.props.IntProperty()

    def execute(self, context):
        # Remove the selected collection by index
        context.scene.bhimax_collections.remove(self.collection_index)
        return {'FINISHED'}

class BHiMAX_AddObjectOperator(bpy.types.Operator):
    bl_idname = "bhimax.add_object"
    bl_label = "Add Object to Collection"
    
    collection_index: bpy.props.IntProperty()
    
    def execute(self, context):
        collection = context.scene.bhimax_collections[self.collection_index]
        selected_objects = bpy.context.selected_objects
        
        # Check if the collection's viewport and render visibility are off
        if collection.hide_viewport and collection.hide_render:
            for obj in selected_objects:
                obj.hide_viewport = True  # Set viewport visibility to off for newly added objects
                obj.hide_render = True  # Set render visibility to off for newly added objects
        else:
            for obj in selected_objects:
                obj.hide_viewport = False  # Set viewport visibility to on for newly added objects
                obj.hide_render = False  # Set render visibility to on for newly added objects
        
        for obj in selected_objects:
            # Check if the object is already in the collection
            if obj not in [item.object for item in collection.objects]:
                obj_property = collection.objects.add()
                obj_property.object = obj
        
        return {'FINISHED'}
class BHiMAX_RemoveObjectOperator(bpy.types.Operator):
    bl_idname = "bhimax.remove_object"
    bl_label = "Remove Object from Collection"
    
    collection_index: bpy.props.IntProperty()
    object_index: bpy.props.IntProperty()
    
    def execute(self, context):
        collection = context.scene.bhimax_collections[self.collection_index]
        
        if 0 <= self.object_index < len(collection.objects):
            collection.objects.remove(self.object_index)
        
        return {'FINISHED'}

class BHiMAX_ToggleViewportVisibilityOperator(bpy.types.Operator):
    bl_idname = "bhimax.toggle_viewport_visibility"
    bl_label = "Toggle Viewport Visibility"
    
    collection_index: bpy.props.IntProperty()

    def execute(self, context):
        collection = context.scene.bhimax_collections[self.collection_index]
        collection.hide_viewport = not collection.hide_viewport
        
        # Synchronize visibility with Blender objects
        for obj_item in collection.objects:
            obj_item.object.hide_viewport = collection.hide_viewport
        
        return {'FINISHED'}

class BHiMAX_ToggleRenderVisibilityOperator(bpy.types.Operator):
    bl_idname = "bhimax.toggle_render_visibility"
    bl_label = "Toggle Render Visibility"
    
    collection_index: bpy.props.IntProperty()

    def execute(self, context):
        collection = context.scene.bhimax_collections[self.collection_index]
        collection.hide_render = not collection.hide_render
        
        # Synchronize visibility with Blender objects
        for obj_item in collection.objects:
            obj_item.object.hide_render = collection.hide_render
        
        return {'FINISHED'}

class BHiMAX_SelectObjectOperator(bpy.types.Operator):
    bl_idname = "bhimax.select_object"
    bl_label = "Toggle Selection"

    collection_index: bpy.props.IntProperty()
    object_index: bpy.props.IntProperty()

    def execute(self, context):
        collection = context.scene.bhimax_collections[self.collection_index]

        if 0 <= self.object_index < len(collection.objects):
            obj_item = collection.objects[self.object_index]
            obj = obj_item.object
            obj.select_set(not obj.select_get())  # Toggle object selection

        return {'FINISHED'}

class BHiMAX_Panel(bpy.types.Panel):
    bl_label = "Collection Editor By BHiMAX"
    bl_idname = "BHiMAX_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Collection Editor'

    def draw(self, context):
        layout = self.layout
        layout.operator("bhimax.new_collection")
        
        # List all the collections with checkboxes and add object button (text)
        for i, collection in enumerate(context.scene.bhimax_collections):
            row = layout.row()
            row.prop(collection, "is_selected", text=collection.name, toggle=True)
            
            if collection.is_selected:
                row.prop(collection, "name", text="")
                
                # Viewport visibility toggle (icon)
                if collection.hide_viewport:
                    viewport_visibility_toggle_icon = 'RESTRICT_VIEW_ON'
                else:
                    viewport_visibility_toggle_icon = 'RESTRICT_VIEW_OFF'
                viewport_visibility_toggle = row.operator("bhimax.toggle_viewport_visibility", text="", icon=viewport_visibility_toggle_icon)
                viewport_visibility_toggle.collection_index = i
                
                # Render visibility toggle (icon)
                if collection.hide_render:
                    render_visibility_toggle_icon = 'RESTRICT_RENDER_ON'
                else:
                    render_visibility_toggle_icon = 'RESTRICT_RENDER_OFF'
                render_visibility_toggle = row.operator("bhimax.toggle_render_visibility", text="", icon=render_visibility_toggle_icon)
                render_visibility_toggle.collection_index = i
                
                # Add object to collection button 
                add_object_button = row.operator("bhimax.add_object", text="", icon='ADD')
                add_object_button.collection_index = i
                
                # Remove collection button
                remove_button = row.operator("bhimax.remove_collection", text="", icon='TRASH')
                remove_button.collection_index = i
                
                   # List objects in collection
                for j, obj_item in enumerate(collection.objects):
                    subrow = layout.row()
                    subrow.prop(obj_item, "object", text="")
                    select_object_button = subrow.operator("bhimax.select_object", text="Select", icon='CHECKBOX_HLT'
                    if obj_item.object.select_get() else 'CHECKBOX_DEHLT')
                    select_object_button.collection_index = i
                    select_object_button.object_index = j
                    
                    # Remove object from collection button (icon)
                    remove_object_button = subrow.operator("bhimax.remove_object", text="", icon='TRASH')
                    remove_object_button.collection_index = i
                    remove_object_button.object_index = j

def register():
    bpy.utils.register_class(BHiMAX_ObjectProperty)
    bpy.utils.register_class(BHiMAX_Collection)
    bpy.utils.register_class(BHiMAX_CollectionCreatorOperator)
    bpy.utils.register_class(BHiMAX_RemoveCollectionOperator)
    bpy.utils.register_class(BHiMAX_AddObjectOperator)
    bpy.utils.register_class(BHiMAX_RemoveObjectOperator)
    bpy.utils.register_class(BHiMAX_ToggleViewportVisibilityOperator)
    bpy.utils.register_class(BHiMAX_ToggleRenderVisibilityOperator)
    bpy.utils.register_class(BHiMAX_SelectObjectOperator)
    bpy.utils.register_class(BHiMAX_Panel)
    
    bpy.types.Scene.bhimax_collections = bpy.props.CollectionProperty(type=BHiMAX_Collection)

def unregister():
    bpy.utils.unregister_class(BHiMAX_ObjectProperty)
    bpy.utils.unregister_class(BHiMAX_Collection)
    bpy.utils.unregister_class(BHiMAX_CollectionCreatorOperator)
    bpy.utils.unregister_class(BHiMAX_RemoveCollectionOperator)
    bpy.utils.unregister_class(BHiMAX_AddObjectOperator)
    bpy.utils.unregister_class(BHiMAX_RemoveObjectOperator)
    bpy.utils.unregister_class(BHiMAX_ToggleViewportVisibilityOperator)
    bpy.utils.unregister_class(BHiMAX_ToggleRenderVisibilityOperator)
    bpy.utils.unregister_class(BHiMAX_SelectObjectOperator)
    bpy.utils.unregister_class(BHiMAX_Panel)
    
    del bpy.types.Scene.bhimax_collections

if __name__ == "__main__":
    register()
