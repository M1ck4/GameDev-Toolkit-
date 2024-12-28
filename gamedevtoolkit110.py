bl_info = {
    "name": "GameDev Pipeline Toolkit 1.10",
    "author": "Michael Neivandt",
    "version": (1, 10),
    "blender": (3, 0, 0),
    "location": "3D View > Tools (N-Panel) > GameDev Toolkit",
    "description": (
        "Fully customizable folder structure, flexible triangulation (off, FBX, "
        "non-destructive, or destructive), FBX export iteration, Substance 3D "
        "naming, duplicate suffix handling, and a preference to disable iteration "
        "if Substance 3D naming is in use."
    ),
    "category": "3D View",
}


import bpy
import os
import sys
import re
import subprocess
from bpy.types import (
    AddonPreferences,
    PropertyGroup,
    Operator,
    Panel,
    UIList,
)
from bpy.props import (
    StringProperty,
    PointerProperty,
    CollectionProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
)


# ------------------------------------------------------------------------------
# 1) PROPERTY GROUP FOR FOLDER NAMES (UIList)
# ------------------------------------------------------------------------------
class GDTFolderName(PropertyGroup):
    """Represents a single folder path in the folder structure list."""
    name: StringProperty(
        name="Folder",
        description="Folder path (relative to the project root)",
        default=""
    )


# ------------------------------------------------------------------------------
# 2) UILIST CLASS TO DISPLAY THE FOLDERS IN THE ADD-ON PREFERENCES
# ------------------------------------------------------------------------------
class GDT_UL_FolderList(UIList):
    """UI list that displays each folder path in the Add-on Preferences."""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "name", text="", emboss=True, icon='FILE_FOLDER')


# ------------------------------------------------------------------------------
# 3) ADD-ON PREFERENCES
# ------------------------------------------------------------------------------
class GDTAddonPreferences(AddonPreferences):
    bl_idname = __name__

    # --- Folder Structure ---
    folder_structure: CollectionProperty(
        type=GDTFolderName,
        name="Folder Structure",
        description="List of sub-folders to create within the project"
    )
    folder_structure_index: IntProperty(
        name="Folder List Index",
        default=0
    )

    # --- Export Settings ---
    export_folder_unity: StringProperty(
        name="Unity Export Folder",
        description="Sub-folder for Unity exports (relative to the project root)",
        default="Unity_Exports"
    )
    export_filename_unity: StringProperty(
        name="Unity Export Base Name",
        description="Base file name for the Unity FBX export",
        default="unity_export"
    )

    export_folder_unreal: StringProperty(
        name="Unreal Export Folder",
        description="Sub-folder for Unreal exports (relative to the project root)",
        default="Unreal_Exports"
    )
    export_filename_unreal: StringProperty(
        name="Unreal Export Base Name",
        description="Base file name for the Unreal FBX export",
        default="unreal_export"
    )

    use_export_iterator: BoolProperty(
        name="Use Export Iterator",
        description="When enabled, each export increments a numeric suffix (e.g., myExport_001.fbx).",
        default=True
    )
    export_iterator: IntProperty(
        name="Export Iterator Counter",
        description="Current export iteration number. Increments after each successful export.",
        default=1,
        min=1
    )

    # --- Triangulation Method ---
    triangulation_method: EnumProperty(
        name="Triangulation Method",
        description=(
            "Choose how meshes are triangulated for export:\n"
            "• Off: no triangulation.\n"
            "• FBX Export Only: relies on the Blender FBX export to triangulate non-destructively.\n"
            "• Non-Destructive Duplication: duplicates your meshes, triangulates the copies, exports them, then removes the copies.\n"
            "• Destructive: permanently triangulates your selected meshes in the scene."
        ),
        items=[
            ('OFF', "Off", "No triangulation performed; export as-is"),
            ('FBX', "FBX Export Only", "Use Blender's FBX export setting to triangulate non-destructively"),
            ('NON_DESTRUCTIVE', "Non-Destructive Duplication", 
             "Duplicate each selected mesh, triangulate duplicates, export them, then remove duplicates"),
            ('DESTRUCTIVE', "Destructive", 
             "Permanently triangulate the selected objects in the scene"),
        ],
        default='FBX'
    )

    # --- Substance 3D Naming ---
    use_substance3d_naming: BoolProperty(
        name="Use Substance 3D Naming",
        description="Enable to add _low / _high suffixes for selected objects and detect these suffixes for exporting",
        default=False
    )
    sp_suffix_low: StringProperty(
        name="Low Suffix",
        description="Suffix to apply for low-poly meshes (e.g. '_low')",
        default="_low"
    )
    sp_suffix_high: StringProperty(
        name="High Suffix",
        description="Suffix to apply for high-poly meshes (e.g. '_high')",
        default="_high"
    )

    # --- Disable Iterator if Substance 3D naming is used
    disable_iterator_when_sp_naming: BoolProperty(
        name="Disable Iterator with Substance 3D Naming",
        description=(
            "If enabled, the export iterator won't be used when "
            "'Use Substance 3D Naming' is active."
        ),
        default=False
    )

    # --- Duplicate Suffix Handling ---
    dupe_suffix_handling: EnumProperty(
        name="Duplicate Suffix Handling",
        description=(
            "How to handle Blender's automatic .001, .002, etc. postfix on duplicated objects:\n"
            "• Keep .xxx: preserves .001 for version tracking.\n"
            "• Remove .xxx: cleans up the name to avoid leftover duplication numbers."
        ),
        items=[
            ('KEEP', "Keep .xxx", "Preserve the .001 postfix (version tracking)"),
            ('REMOVE', "Remove .xxx", "Strip .001 or .002 from the object name"),
        ],
        default='KEEP'
    )

    def draw(self, context):
        layout = self.layout

        # Subfolder List
        box = layout.box()
        box.label(text="Subfolder Setup", icon='FILE_FOLDER')
        row = box.row()
        row.template_list(
            "GDT_UL_FolderList",
            "",
            self,
            "folder_structure",
            self,
            "folder_structure_index",
            rows=5
        )

        col = row.column(align=True)
        col.operator("gdt.add_folder", icon="ADD", text="")
        col.operator("gdt.remove_folder", icon="REMOVE", text="")
        col.separator()
        col.operator("gdt.move_folder_up", icon="TRIA_UP", text="")
        col.operator("gdt.move_folder_down", icon="TRIA_DOWN", text="")

        box.label(text="Use + / - to add/remove, arrows to reorder folders")

        # Export Settings
        box2 = layout.box()
        box2.label(text="Export Settings", icon='EXPORT')
        box2.prop(self, "export_folder_unity")
        box2.prop(self, "export_filename_unity")
        box2.prop(self, "export_folder_unreal")
        box2.prop(self, "export_filename_unreal")
        box2.prop(self, "use_export_iterator")
        box2.prop(self, "export_iterator")

        # Triangulation Method
        box3 = layout.box()
        box3.label(text="Mesh Triangulation", icon='MESH_DATA')
        box3.prop(self, "triangulation_method")

        # Substance 3D Naming
        box4 = layout.box()
        box4.label(text="Substance 3D Naming", icon='FILE_TEXT')
        box4.prop(self, "use_substance3d_naming")
        if self.use_substance3d_naming:
            box4.prop(self, "sp_suffix_low")
            box4.prop(self, "sp_suffix_high")
            box4.label(text="Operators in N-Panel > GameDev Toolkit > Substance Tools")

        # Toggle to disable iteration if Substance 3D naming is in use
        box5 = layout.box()
        box5.label(text="Conditional Iterator", icon='MODIFIER')
        box5.prop(self, "disable_iterator_when_sp_naming")

        # Duplicate Suffix Handling
        box6 = layout.box()
        box6.label(text="Duplicate Suffix Handling", icon='OUTLINER_OB_GROUP_INSTANCE')
        box6.prop(self, "dupe_suffix_handling")


# ------------------------------------------------------------------------------
# 4) SCENE PROPERTY GROUP
# ------------------------------------------------------------------------------
class GDTProperties(PropertyGroup):
    """Properties stored at the scene level, for setting project path & name."""
    root_path: StringProperty(
        name="Root Path",
        description="Path where your main project folder will be created (e.g. your Unity/Unreal project)",
        default="",
        subtype='DIR_PATH'
    )
    project_name: StringProperty(
        name="Project Name",
        description="Main folder name for your project (e.g. 'SciFiWeapon')",
        default="NewPropProject"
    )


# ------------------------------------------------------------------------------
# 5) OPERATORS FOR MANAGING FOLDER LIST
# ------------------------------------------------------------------------------
class GDT_OT_AddFolder(Operator):
    """Add a new folder path to the list."""
    bl_idname = "gdt.add_folder"
    bl_label = "Add Folder Path"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        new_item = prefs.folder_structure.add()
        new_item.name = "NewFolder"
        prefs.folder_structure_index = len(prefs.folder_structure) - 1
        return {'FINISHED'}


class GDT_OT_RemoveFolder(Operator):
    """Remove the selected folder path from the list."""
    bl_idname = "gdt.remove_folder"
    bl_label = "Remove Folder Path"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        idx = prefs.folder_structure_index

        if 0 <= idx < len(prefs.folder_structure):
            prefs.folder_structure.remove(idx)
            prefs.folder_structure_index = min(idx, len(prefs.folder_structure) - 1)

        return {'FINISHED'}


class GDT_OT_MoveFolderUp(Operator):
    """Move the selected folder path up in the list."""
    bl_idname = "gdt.move_folder_up"
    bl_label = "Move Folder Up"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        idx = prefs.folder_structure_index

        if idx <= 0:
            return {'CANCELLED'}

        prefs.folder_structure.move(idx, idx - 1)
        prefs.folder_structure_index -= 1
        return {'FINISHED'}


class GDT_OT_MoveFolderDown(Operator):
    """Move the selected folder path down in the list."""
    bl_idname = "gdt.move_folder_down"
    bl_label = "Move Folder Down"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        idx = prefs.folder_structure_index

        if idx >= len(prefs.folder_structure) - 1:
            return {'CANCELLED'}

        prefs.folder_structure.move(idx, idx + 1)
        prefs.folder_structure_index += 1
        return {'FINISHED'}


# ------------------------------------------------------------------------------
# 6) HELPER FUNCTIONS
# ------------------------------------------------------------------------------
def triangulate_selected_objects():
    """
    Triangulates all selected MESH objects in a destructive manner.
    Ensures the user is in object mode afterwards.
    """
    selected_objects = bpy.context.selected_objects
    original_mode = None
    if bpy.context.active_object:
        original_mode = bpy.context.active_object.mode

    for obj in selected_objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            bpy.ops.object.mode_set(mode='OBJECT')

    # Optionally restore original mode
    if original_mode and bpy.context.active_object:
        bpy.ops.object.mode_set(mode=original_mode)


def non_destructive_triangulate_selected():
    """
    Creates duplicates of selected mesh objects, triangulates the duplicates,
    and returns a list of the new triangulated objects.
    """
    temp_collection_name = "Temp_Triangulated"
    temp_collection = bpy.data.collections.get(temp_collection_name)
    if not temp_collection:
        temp_collection = bpy.data.collections.new(temp_collection_name)
        bpy.context.scene.collection.children.link(temp_collection)

    triangulated_objects = []
    current_selection = bpy.context.selected_objects

    for obj in current_selection:
        if obj.type == 'MESH':
            # Duplicate object + mesh data
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            triangulated_objects.append(new_obj)

            # Link to temp collection
            temp_collection.objects.link(new_obj)

            # Triangulate in Edit Mode
            bpy.context.view_layer.objects.active = new_obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            bpy.ops.object.mode_set(mode='OBJECT')

    return triangulated_objects


def cleanup_triangulated_objects():
    """
    Removes all objects in the temporary triangulated collection.
    """
    temp_collection_name = "Temp_Triangulated"
    temp_collection = bpy.data.collections.get(temp_collection_name)
    if temp_collection:
        for obj in temp_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(temp_collection)


def clean_blender_dupe_suffix(name: str) -> str:
    """
    Removes any Blender duplication suffix like .001, .002, etc.
    Only if it's at the end of the string, e.g. 'cube.001' -> 'cube'.
    """
    return re.sub(r"\.\d{3}$", "", name)


def remove_substance_suffix(obj_name, sp_suffix_low, sp_suffix_high):
    """
    Removes the _low or _high suffix from the given name if it is present.
    (Only if the name strictly ends with that suffix.)
    """
    if obj_name.endswith(sp_suffix_low):
        obj_name = obj_name[:-len(sp_suffix_low)]
    elif obj_name.endswith(sp_suffix_high):
        obj_name = obj_name[:-len(sp_suffix_high)]
    return obj_name


def detect_suffix_for_export(selected_objs, low_suffix, high_suffix):
    """
    Returns:
    - low_suffix if ALL MESH objects end with that suffix
    - high_suffix if ALL MESH objects end with that suffix
    - "" otherwise (mixed or no suffix)
    """
    if not selected_objs:
        return ""

    mesh_objs = [o for o in selected_objs if o.type == 'MESH']
    if not mesh_objs:
        return ""

    if all(obj.name.endswith(low_suffix) for obj in mesh_objs):
        return low_suffix

    if all(obj.name.endswith(high_suffix) for obj in mesh_objs):
        return high_suffix

    # Otherwise no consistent suffix
    return ""


# ------------------------------------------------------------------------------
# 7) MAIN OPERATORS: CREATE FOLDERS, EXPORT, OPEN PROJECT, SUBSTANCE 3D NAMING
# ------------------------------------------------------------------------------
class GDT_OT_CreateFolders(Operator):
    """Creates a folder structure based on the add-on preferences."""
    bl_idname = "gdt.create_folders"
    bl_label = "Create Folder Structure"

    def execute(self, context):
        props = context.scene.gdt_properties
        prefs = context.preferences.addons[__name__].preferences

        project_path = os.path.join(props.root_path, props.project_name)

        # Create each sub-folder from the list
        for folder_item in prefs.folder_structure:
            folder_name = folder_item.name.strip()
            if not folder_name:
                continue
            folder_path = os.path.join(project_path, folder_name)
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                self.report({'ERROR'}, f"Could not create folder: {folder_path}\n{e}")
                return {'CANCELLED'}

        self.report({'INFO'}, f"Folder structure created at: {project_path}")
        return {'FINISHED'}


class GDT_OT_ExportUnity(Operator):
    """Exports selected objects with typical Unity-friendly FBX settings."""
    bl_idname = "gdt.export_unity"
    bl_label = "Export for Unity"

    def execute(self, context):
        props = context.scene.gdt_properties
        prefs = context.preferences.addons[__name__].preferences

        project_root = os.path.join(props.root_path, props.project_name)
        export_dir = os.path.join(project_root, prefs.export_folder_unity)
        os.makedirs(export_dir, exist_ok=True)

        # Determine iteration usage
        use_iteration = prefs.use_export_iterator
        if prefs.disable_iterator_when_sp_naming and prefs.use_substance3d_naming:
            use_iteration = False

        # Detect suffix from selection (only if using Substance 3D naming)
        selection = bpy.context.selected_objects
        suffix_found = ""
        if prefs.use_substance3d_naming:
            suffix_found = detect_suffix_for_export(
                selection,
                prefs.sp_suffix_low,
                prefs.sp_suffix_high
            )

        # Build filename
        filename = prefs.export_filename_unity  # e.g. "unity_export"
        if suffix_found:
            filename += suffix_found  # e.g. "unity_export_low" or "unity_export_high"

        if use_iteration:
            filename += f"_{prefs.export_iterator:03d}"

        filename += ".fbx"
        export_path = os.path.join(export_dir, filename)

        # Triangulation handling
        triang_mode = prefs.triangulation_method

        try:
            if triang_mode == 'NON_DESTRUCTIVE':
                non_destructive_triangulate_selected()
            elif triang_mode == 'DESTRUCTIVE':
                triangulate_selected_objects()

            bpy.ops.export_scene.fbx(
                filepath=export_path,
                use_selection=True,
                apply_unit_scale=True,
                apply_scale_options='FBX_SCALE_NONE',
                bake_space_transform=False,
                object_types={'MESH'},
                use_mesh_modifiers=(triang_mode == 'FBX'),  # FBX mode uses built-in triangulation
                mesh_smooth_type='FACE',
                axis_forward='-Z',
                axis_up='Y'
            )
        except Exception as e:
            self.report({'ERROR'}, f"FBX Export Failed: {e}")
            return {'CANCELLED'}
        finally:
            # Cleanup if we used NON_DESTRUCTIVE mode
            if triang_mode == 'NON_DESTRUCTIVE':
                cleanup_triangulated_objects()

        # Increment iterator if used
        if use_iteration:
            prefs.export_iterator += 1

        self.report({'INFO'}, f"Exported for Unity: {export_path}")
        return {'FINISHED'}


class GDT_OT_ExportUnreal(Operator):
    """Exports selected objects with typical Unreal-friendly FBX settings."""
    bl_idname = "gdt.export_unreal"
    bl_label = "Export for Unreal"

    def execute(self, context):
        props = context.scene.gdt_properties
        prefs = context.preferences.addons[__name__].preferences

        project_root = os.path.join(props.root_path, props.project_name)
        export_dir = os.path.join(project_root, prefs.export_folder_unreal)
        os.makedirs(export_dir, exist_ok=True)

        # Determine iteration usage
        use_iteration = prefs.use_export_iterator
        if prefs.disable_iterator_when_sp_naming and prefs.use_substance3d_naming:
            use_iteration = False

        # Detect suffix from selection (only if using Substance 3D naming)
        selection = bpy.context.selected_objects
        suffix_found = ""
        if prefs.use_substance3d_naming:
            suffix_found = detect_suffix_for_export(
                selection,
                prefs.sp_suffix_low,
                prefs.sp_suffix_high
            )

        # Build filename
        filename = prefs.export_filename_unreal  # e.g. "unreal_export"
        if suffix_found:
            filename += suffix_found  # e.g. "unreal_export_low" or "unreal_export_high"

        if use_iteration:
            filename += f"_{prefs.export_iterator:03d}"

        filename += ".fbx"
        export_path = os.path.join(export_dir, filename)

        # Triangulation handling
        triang_mode = prefs.triangulation_method

        try:
            if triang_mode == 'NON_DESTRUCTIVE':
                non_destructive_triangulate_selected()
            elif triang_mode == 'DESTRUCTIVE':
                triangulate_selected_objects()

            bpy.ops.export_scene.fbx(
                filepath=export_path,
                use_selection=True,
                apply_unit_scale=True,
                apply_scale_options='FBX_SCALE_NONE',
                bake_space_transform=False,
                object_types={'MESH'},
                use_mesh_modifiers=(triang_mode == 'FBX'),  # FBX mode uses built-in triangulation
                mesh_smooth_type='FACE',
                axis_forward='-Z',
                axis_up='Y'
            )
        except Exception as e:
            self.report({'ERROR'}, f"FBX Export Failed: {e}")
            return {'CANCELLED'}
        finally:
            # Cleanup if we used NON_DESTRUCTIVE mode
            if triang_mode == 'NON_DESTRUCTIVE':
                cleanup_triangulated_objects()

        # Increment iterator if used
        if use_iteration:
            prefs.export_iterator += 1

        self.report({'INFO'}, f"Exported for Unreal: {export_path}")
        return {'FINISHED'}


class GDT_OT_OpenProjectFolder(Operator):
    """Open the project folder in your system's file explorer."""
    bl_idname = "gdt.open_project_folder"
    bl_label = "Open Project Folder"

    def execute(self, context):
        props = context.scene.gdt_properties
        project_path = os.path.join(props.root_path, props.project_name)

        if not os.path.exists(project_path):
            self.report({'ERROR'}, "Project folder does not exist. Create folder structure first.")
            return {'CANCELLED'}

        try:
            if sys.platform == "win32":
                os.startfile(project_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", project_path])
            else:
                subprocess.run(["xdg-open", project_path])
        except Exception as e:
            self.report({'ERROR'}, f"Could not open folder: {project_path}\n{e}")
            return {'CANCELLED'}

        return {'FINISHED'}


# ------------------------------------------------------------------------------
# 8) SUBSTANCE 3D NAMING OPERATORS (FIXED ORDER OF DUPLICATE SUFFIX REMOVAL)
# ------------------------------------------------------------------------------
class GDT_OT_RenameSubstanceLow(Operator):
    """Rename selected objects to use the '_low' suffix."""
    bl_idname = "gdt.rename_substance_low"
    bl_label = "Rename Selected (Low)"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences

        if not prefs.use_substance3d_naming:
            self.report({'INFO'}, "Substance 3D naming is disabled in preferences.")
            return {'CANCELLED'}

        suffix = prefs.sp_suffix_low
        count = 0
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                # 1) Remove .001, etc. if user selected "REMOVE"
                temp_name = obj.name
                if prefs.dupe_suffix_handling == 'REMOVE':
                    temp_name = clean_blender_dupe_suffix(temp_name)

                # 2) Remove old _low or _high suffix
                temp_name = remove_substance_suffix(
                    temp_name,
                    prefs.sp_suffix_low,
                    prefs.sp_suffix_high
                )

                # 3) Append the chosen "_low" suffix
                obj.name = temp_name + suffix
                count += 1

        self.report({'INFO'}, f"Renamed {count} object(s) with '{suffix}' suffix.")
        return {'FINISHED'}


class GDT_OT_RenameSubstanceHigh(Operator):
    """Rename selected objects to use the '_high' suffix."""
    bl_idname = "gdt.rename_substance_high"
    bl_label = "Rename Selected (High)"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences

        if not prefs.use_substance3d_naming:
            self.report({'INFO'}, "Substance 3D naming is disabled in preferences.")
            return {'CANCELLED'}

        suffix = prefs.sp_suffix_high
        count = 0
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                # 1) Remove .001, etc. if user selected "REMOVE"
                temp_name = obj.name
                if prefs.dupe_suffix_handling == 'REMOVE':
                    temp_name = clean_blender_dupe_suffix(temp_name)

                # 2) Remove old _low or _high suffix
                temp_name = remove_substance_suffix(
                    temp_name,
                    prefs.sp_suffix_low,
                    prefs.sp_suffix_high
                )

                # 3) Append the chosen "_high" suffix
                obj.name = temp_name + suffix
                count += 1

        self.report({'INFO'}, f"Renamed {count} object(s) with '{suffix}' suffix.")
        return {'FINISHED'}


# ------------------------------------------------------------------------------
# 9) UI PANEL (N-PANEL) FOR SCENE-LEVEL ACTIONS
# ------------------------------------------------------------------------------
class GDT_PT_MainPanel(Panel):
    bl_idname = "GDT_PT_main_panel"
    bl_label = "GameDev Toolkit"
    bl_category = "GameDev Toolkit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        props = context.scene.gdt_properties
        prefs = context.preferences.addons[__name__].preferences

        # Project setup
        box = layout.box()
        box.label(text="Project Setup", icon='FILE_FOLDER')
        box.prop(props, "root_path")
        box.prop(props, "project_name")

        row = box.row()
        row.operator("gdt.create_folders", icon='NEWFOLDER')
        row.operator("gdt.open_project_folder", icon='FILE_FOLDER')

        # Export options
        box2 = layout.box()
        box2.label(text="Export Options", icon='EXPORT')
        row = box2.row()
        row.operator("gdt.export_unity", icon='OUTLINER_OB_MESH')
        row.operator("gdt.export_unreal", icon='OUTLINER_OB_MESH')

        # Substance 3D Tools
        if prefs.use_substance3d_naming:
            box3 = layout.box()
            box3.label(text="Substance 3D Tools", icon='FILE_TEXT')
            row2 = box3.row()
            row2.operator("gdt.rename_substance_low", icon='OUTLINER_OB_MESH')
            row2.operator("gdt.rename_substance_high", icon='OUTLINER_OB_MESH')
        else:
            layout.label(text="(Substance 3D naming is disabled in Preferences)")


# ------------------------------------------------------------------------------
# REGISTER / UNREGISTER
# ------------------------------------------------------------------------------
classes = (
    # 1) FolderItem & UIList
    GDTFolderName,
    GDT_UL_FolderList,

    # 2) Addon Preferences
    GDTAddonPreferences,

    # 3) Scene PropertyGroup
    GDTProperties,

    # 4) Operators for FolderList
    GDT_OT_AddFolder,
    GDT_OT_RemoveFolder,
    GDT_OT_MoveFolderUp,
    GDT_OT_MoveFolderDown,

    # 5) Main Operators
    GDT_OT_CreateFolders,
    GDT_OT_ExportUnity,
    GDT_OT_ExportUnreal,
    GDT_OT_OpenProjectFolder,

    # 6) Substance 3D Operators (with the new fix)
    GDT_OT_RenameSubstanceLow,
    GDT_OT_RenameSubstanceHigh,

    # 7) Main Panel
    GDT_PT_MainPanel
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gdt_properties = PointerProperty(type=GDTProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.gdt_properties


if __name__ == "__main__":
    register()
