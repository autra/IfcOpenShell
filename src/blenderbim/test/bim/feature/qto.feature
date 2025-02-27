@qto
Feature: Qto

Scenario: Calculate circle radius
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_circle_radius"
    Then "scene.BIMQtoProperties.qto_result" is "1.732"

Scenario: Calculate edge lengths
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_edge_lengths"
    Then "scene.BIMQtoProperties.qto_result" is "24.0"

Scenario: Calculate face areas
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_face_areas"
    Then "scene.BIMQtoProperties.qto_result" is "24.0"

Scenario: Calculate object volumes
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_object_volumes"
    Then "scene.BIMQtoProperties.qto_result" is "8.0"

Scenario: Execute qto method - formwork areas
    Given an empty Blender session
    And I add a cube
    And I add a cube of size "1" at "1,0,0"
    And the object "Cube" is selected
    And additionally the object "Cube.001" is selected
    When I press "bim.calculate_formwork_area"
    Then "scene.BIMQtoProperties.qto_result" is "21.5"

Scenario: Execute qto method - side formwork areas
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_side_formwork_area"
    Then "scene.BIMQtoProperties.qto_result" is "16.0"

Scenario: Calculate all quantities
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.assign_class(ifc_class='IfcWall', predefined_type='SOLIDWALL')"
    When I press "bim.perform_quantity_take_off"
    And the variable "qset_id" is "{ifc}.by_type('IfcElementQuantity')[0].id()"
    And I press "bim.enable_pset_editing(pset_id={qset_id}, obj='IfcWall/Cube', obj_type='Object')"
    Then "active_object.PsetProperties.active_pset_name" is "Qto_WallBaseQuantities"
    And "active_object.PsetProperties.properties['Length'].metadata.float_value" is roughly "2000.0"
