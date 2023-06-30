import bpy

bl_info = {
    "name": "mixamo combiner",
    "author": "elliot mckenzie",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar",
    "description": "Combine mixamo animations in x and y space",
    "category": "Object"
}

class OBJECT_OT_my_button(bpy.types.Operator):
    bl_idname = "object.my_button"
    bl_label = "My Button"
    bl_description = "Click this button to perform an action"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Your code here
        # Get the active object (assuming it's an armature)
        import bpy
        obj = bpy.context.active_object

        # Ensure the object is an armature
        if obj.type != 'ARMATURE':
            raise ValueError("Active object is not an armature.")

        # Get the armature
        armature = obj.data

        # Get the bone by name
        bone_name = "mixamorig:Hips"
        bone = armature.bones.get(bone_name)

        if not bone:
            raise ValueError("Bone '{}' not found.".format(bone_name))

        # Get the selected keyframes for the bone's location
        action = obj.animation_data.action
        fcurves = [fc for fc in action.fcurves if fc.data_path == 'pose.bones["{}"].location'.format(bone_name)]
        x_fcurve = next((fc for fc in fcurves if fc.array_index == 0), None)
        z_fcurve = next((fc for fc in fcurves if fc.array_index == 2), None)

        if not x_fcurve or not z_fcurve:
            raise ValueError("No selected keyframes found for bone '{}'.".format(bone_name))

        # Find the location values of the first keyframe before the selected keyframes
        prev_x_location = None
        prev_z_location = None

        for kf in x_fcurve.keyframe_points:
            if kf.co[0] >= action.frame_range.x:
                if kf.co[0] >= action.frame_range.y:
                    break
                elif kf.select_control_point:
                    break
                prev_x_location = kf.co[1]

        for kf in z_fcurve.keyframe_points:
            if kf.co[0] >= action.frame_range.x:
                if kf.co[0] >= action.frame_range.y:
                    break
                elif kf.select_control_point:
                    break
                prev_z_location = kf.co[1]

        # If no previous keyframes found, raise an error
        if prev_x_location is None or prev_z_location is None:
            raise ValueError("No previous keyframes found for bone '{}'.".format(bone_name))

        # Add the location values of the previous keyframes to the selected keyframes
        for kf in x_fcurve.keyframe_points:
            if kf.select_control_point:
                kf.co[1] += prev_x_location

        for kf in z_fcurve.keyframe_points:
            if kf.select_control_point:
                kf.co[1] += prev_z_location

        # Update the viewport to reflect the changes
        bpy.context.view_layer.update()

        self.report({'INFO'}, "Button clicked!")
        return {'FINISHED'}

class VIEW3D_PT_my_panel(bpy.types.Panel):
    bl_label = "Mixamo Combiner"
    bl_idname = "VIEW3D_PT_my_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mixamo Combiner"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.my_button", text="Fix placement")


def register():
    bpy.utils.register_class(OBJECT_OT_my_button)
    bpy.utils.register_class(VIEW3D_PT_my_panel)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_my_button)
    bpy.utils.unregister_class(VIEW3D_PT_my_panel)


if __name__ == "__main__":
    register()
