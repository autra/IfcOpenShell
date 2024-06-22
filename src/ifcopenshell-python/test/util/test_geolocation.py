# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import pytest
import numpy as np
import test.bootstrap
import ifcopenshell.api.root
import ifcopenshell.api.context
import ifcopenshell.api.georeference
import ifcopenshell.util.geolocation as subject


class TestXYZ2ENH(test.bootstrap.IFC4):
    def test_converting_from_a_local_xyz_point_to_a_global_easting_northing_height(self):
        assert subject.xyz2enh(0, 0, 0, 0, 0, 0, 1, 0) == (0, 0, 0)
        assert subject.xyz2enh(0, 0, 0, 1, 2, 3, 1, 0) == (1, 2, 3)
        assert subject.xyz2enh(0, 0, 0, 1, 2, 3, 0, 1) == (1, 2, 3)
        assert np.allclose(subject.xyz2enh(1, 1, 0, 1, 2, 3, 1, 0), (2, 3, 3))
        assert np.allclose(subject.xyz2enh(1, 1, 0, 1, 2, 3, 1, 0, 2), (3, 4, 3))
        assert np.allclose(subject.xyz2enh(1, 1, 1, 1, 2, 3, 1, 0, 2, 2, 3, 4), (5, 8, 11))
        assert np.allclose(subject.xyz2enh(1, 1, 0, 1, 2, 3, 0, 1), (0, 3, 3))


class TestENH2XYZ(test.bootstrap.IFC4):
    def test_converting_from_a_global_easting_northing_height_to_a_local_xyz_point(self):
        assert subject.enh2xyz(0, 0, 0, 0, 0, 0, 1, 0) == (0, 0, 0)
        assert subject.enh2xyz(1, 2, 3, 1, 2, 3, 1, 0) == (0, 0, 0)
        assert subject.enh2xyz(1, 2, 3, 1, 2, 3, 0, 1) == (0, 0, 0)
        assert np.allclose(subject.enh2xyz(2, 3, 3, 1, 2, 3, 1, 0), (1, 1, 0))
        assert np.allclose(subject.enh2xyz(3, 4, 3, 1, 2, 3, 1, 0, 2), (1, 1, 0))
        assert np.allclose(subject.enh2xyz(5, 8, 11, 1, 2, 3, 1, 0, 2, 2, 3, 4), (1, 1, 1))
        assert np.allclose(subject.enh2xyz(0, 3, 3, 1, 2, 3, 0, 1), (1, 1, 0))


class TestZ2E(test.bootstrap.IFC4):
    def test_converting_from_a_local_z_to_a_global_elevation(self):
        assert subject.z2e(0) == 0
        assert subject.z2e(0, 0, 1, 1) == 0
        assert subject.z2e(0, 2) == 2
        assert subject.z2e(1, 2) == 3
        assert subject.z2e(1000, 2, 0.001) == 3
        assert np.isclose(subject.z2e(1000, 2, 0.001, 0.9), 2.9)


class TestAutoXYZ2ENH(test.bootstrap.IFC4):
    def test_no_georeferencing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        assert subject.auto_xyz2enh(self.file, 0, 0, 0) == (0, 0, 0)
        assert subject.auto_xyz2enh(self.file, 1, 2, 3) == (1, 2, 3)

    def test_map_conversion(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            map_conversion={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        assert subject.auto_xyz2enh(self.file, 0, 0, 0) == (1, 2, 3)
        assert subject.auto_xyz2enh(self.file, 1, 3, 5) == (2, 5, 8)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, map_conversion={"Scale": 0.001})
        assert subject.auto_xyz2enh(self.file, 1000, 1000, 0) == (2, 3, 3)
        assert subject.auto_xyz2enh(self.file, 1000, 1000, 0, should_return_in_map_units=False) == (2000, 3000, 3000)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, map_conversion={"XAxisAbscissa": 0, "XAxisOrdinate": 1}
        )
        assert np.allclose(subject.auto_xyz2enh(self.file, 1000, 1000, 0), (0, 3, 3))


class TestAutoENH2XYZ(test.bootstrap.IFC4):
    def test_no_georeferencing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        assert subject.auto_enh2xyz(self.file, 0, 0, 0) == (0, 0, 0)
        assert subject.auto_enh2xyz(self.file, 1, 2, 3) == (1, 2, 3)

    def test_map_conversion(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            map_conversion={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        assert subject.auto_enh2xyz(self.file, 1, 2, 3) == (0, 0, 0)
        assert subject.auto_enh2xyz(self.file, 2, 5, 8) == (1, 3, 5)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, map_conversion={"Scale": 0.001})
        assert np.allclose(subject.auto_enh2xyz(self.file, 2, 3, 3), (1000, 1000, 0))
        assert np.allclose(
            subject.auto_enh2xyz(self.file, 2000, 3000, 3000, is_specified_in_map_units=False), (1000, 1000, 0)
        )
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, map_conversion={"XAxisAbscissa": 0, "XAxisOrdinate": 1}
        )
        assert np.allclose(subject.auto_enh2xyz(self.file, 0, 3, 3), (1000, 1000, 0))


class TestAutoZ2E(test.bootstrap.IFC4):
    def test_no_georeferencing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        assert subject.auto_z2e(self.file, 0) == 0
        assert subject.auto_z2e(self.file, 1) == 1

    def test_map_conversion(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            map_conversion={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        assert subject.auto_z2e(self.file, 0) == 3
        assert subject.auto_z2e(self.file, 5) == 8
        ifcopenshell.api.georeference.edit_georeferencing(self.file, map_conversion={"Scale": 0.001})
        assert np.isclose(subject.auto_z2e(self.file, 0), 3)
        assert np.isclose(subject.auto_z2e(self.file, 0, should_return_in_map_units=False), 3000)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, map_conversion={"XAxisAbscissa": 0, "XAxisOrdinate": 1}
        )
        assert np.isclose(subject.auto_z2e(self.file, 0), 3)


class TestLocal2Global(test.bootstrap.IFC4):
    def test_converting_from_a_local_matrix_to_a_global_matrix(self):
        m = np.eye(4)
        m2 = np.eye(4)
        assert np.allclose(subject.local2global(m, 0, 0, 0, 1.0, 0.0), m2)

        m2[:, 3][0:3] = [1, 2, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 1.0, 0.0), m2)

        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 0.0, 1.0), m2)

        m[:, 3][0:3] = [1, 1, 0]
        m2 = np.eye(4)
        m2[:, 3][0:3] = [2, 3, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 1.0, 0.0), m2)

        m2[:, 3][0:3] = [3, 4, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 1.0, 0.0, 2), m2)

        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        m2[:, 3][0:3] = [0, 3, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 0.0, 1.0), m2)


class TestLocal2GlobalIfc4X3(test.bootstrap.IFC4):
    def test_converting_from_a_local_matrix_to_a_global_matrix(self):
        m = np.eye(4)
        m2 = np.eye(4)
        assert np.allclose(subject.local2global_ifc4x3(m, 0, 0, 0, 1.0, 0.0), m2)

        m2[:, 3][0:3] = [1, 2, 3]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 1.0, 0.0), m2)

        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 0.0, 1.0), m2)

        m[:, 3][0:3] = [1, 1, 0]
        m2 = np.eye(4)
        m2[:, 3][0:3] = [2, 3, 3]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 1.0, 0.0), m2)

        m2[:, 3][0:3] = [3, 4, 3]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 1.0, 0.0, 2), m2)

        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        m2[:, 3][0:3] = [0, 3, 3]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 0.0, 1.0), m2)

        m[:, 3][0:3] = [1, 1, 1]
        m2 = np.eye(4)
        m2[:, 3][0:3] = [5, 8, 11]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 1.0, 0.0, 2, 2, 3, 4), m2)
