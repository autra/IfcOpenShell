# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool
import blenderbim.core.spatial
import blenderbim.core.aggregate
from blenderbim.bim.ifc import IfcStore


class OpenPieClass(bpy.types.Operator):
    bl_idname = "bim.open_pie_class"
    bl_label = "Open Pie Class"
    bl_description = "Assign the IFC Class to the selected objects"

    @classmethod
    def poll(cls, context):
        if not context.active_object and not context.selected_objects:
            cls.poll_message_set("No object selected.")
            return False
        return True

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_PIE_bim_class")
        return {"FINISHED"}


class PieAddOpening(bpy.types.Operator):
    bl_idname = "bim.pie_add_opening"
    bl_label = "Add Opening"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        if len(context.selected_objects) == 2:
            opening_name = None
            obj_name = None
            for obj in context.selected_objects:
                if "IfcOpeningElement" in obj.name or not obj.BIMObjectProperties.ifc_definition_id:
                    opening_name = obj.name
                elif len(obj.children) == 1 and not obj.children[0].BIMObjectProperties.ifc_definition_id:
                    opening_name = obj.children[0].name
                else:
                    obj_name = obj.name
            bpy.ops.bim.add_opening(obj=obj_name, opening=opening_name)
        return {"FINISHED"}


class VIEW3D_MT_PIE_bim(bpy.types.Menu):
    bl_label = "Geometry"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("bim.edit_object_placement")
        pie.operator("bim.update_representation").ifc_representation_class = ""
        pie.operator("bim.pie_add_opening")
        pie.operator("bim.open_pie_class", text="Assign IFC Class")
        pie.operator("bim.aggregate_assign_object", text="Assign Aggregation")
        pie.operator("bim.aggregate_unassign_object", text="Unassign Aggregation")


class VIEW3D_MT_PIE_bim_class(bpy.types.Menu):
    bl_label = "Class"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("bim.assign_class", text="IfcWall").ifc_class = "IfcWall"
        pie.operator("bim.assign_class", text="IfcSlab").ifc_class = "IfcSlab"
        pie.operator("bim.assign_class", text="IfcStair").ifc_class = "IfcStair"
        pie.operator("bim.assign_class", text="IfcDoor").ifc_class = "IfcDoor"
        pie.operator("bim.assign_class", text="IfcWindow").ifc_class = "IfcWindow"
        pie.operator("bim.assign_class", text="IfcColumn").ifc_class = "IfcColumn"
        pie.operator("bim.assign_class", text="IfcBeam").ifc_class = "IfcBeam"
