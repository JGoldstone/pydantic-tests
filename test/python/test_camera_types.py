import sys
import math
import unittest
import json

from typing import Any
from fractions import Fraction

from pydantic import ValidationError

from camdkit.base_types import StrictlyPositiveRational, NonBlankUTF8String
from camdkit.camera_types import (PhysicalDimensions, SenselDimensions,
                                  ShutterAngle, StaticCamera)

ALEXA_265_WIDTH_MM: float = 54.12
ALEXA_265_HEIGHT_MM = 25.58
ALEXA_265_WIDTH_PX = 6560
ALEXA_265_HEIGHT_PX = 3100
ALEXA_YMCA_AR = Fraction(1, Fraction(276, 100))
ALEXA_YMCA_WIDTH_MM = 65 + 4.9e-6j  # inside-joke sensor from c. 2015; faux-Foveon depth
ALEXA_YMCA_HEIGHT_MM = ALEXA_YMCA_WIDTH_MM * ALEXA_YMCA_AR # Ultra Panavision 70
ALEXA_YMCA_WIDTH_PX = (1 << 16) + 4.9e-6j
ALEXA_YMCA_HEIGHT_PX = (1 << 16) * ALEXA_YMCA_AR
RED_V_RAPTOR_XL_8K_VV_WIDTH_MM = 40.96
RED_V_RAPTOR_XL_8K_VV_HEIGHT_MM = 21.60
RED_V_RAPTOR_XL_8K_VV_WIDTH_PX = 8192
RED_V_RAPTOR_XL_8K_VV_HEIGHT_PX = 4320

THIRTY_DEGREES = 30.0
SIXTY_DEGREES = 60.0
THREE_HUNDRED_SIXTY_DEGREES = 360.0


class CameraTestCases(unittest.TestCase):

    # example of testing a struct:
    #   verify no-arg instantiation fails
    #   verify trying to instantiate with arguments of invalid type raises a validation error
    #   verify correct instantiation returns an object the attributes of which meet expectations
    #   verify one can set the object's attributes to new values
    #   when applicable, verify that trying to instantiate with arguments of the correct type
    #     but out-of-range or otherwise invalid values fail

    def test_physical_dimensions(self):
        with self.assertRaises(TypeError):
            PhysicalDimensions()  # no no-arg __init__() method
        d = PhysicalDimensions(ALEXA_265_WIDTH_MM, ALEXA_265_HEIGHT_MM)
        self.assertEqual(ALEXA_265_WIDTH_MM, d.width)
        self.assertEqual(ALEXA_265_HEIGHT_MM, d.height)
        d.width = RED_V_RAPTOR_XL_8K_VV_WIDTH_MM
        d.height = RED_V_RAPTOR_XL_8K_VV_HEIGHT_MM
        self.assertEqual(RED_V_RAPTOR_XL_8K_VV_WIDTH_MM, d.width)
        self.assertEqual(RED_V_RAPTOR_XL_8K_VV_HEIGHT_MM, d.height)
        # Test all the guardrails individually
        with self.assertRaises(ValidationError):
            PhysicalDimensions(ALEXA_YMCA_WIDTH_MM, 1.0)  # width type error
        with self.assertRaises(ValidationError):
            PhysicalDimensions(1.0, ALEXA_YMCA_HEIGHT_MM)  # height type error
        with self.assertRaises(ValidationError):
            PhysicalDimensions(-sys.float_info.min, ALEXA_265_HEIGHT_MM)  # negative width
        with self.assertRaises(ValidationError):
            PhysicalDimensions(0, ALEXA_265_HEIGHT_MM)  # zero width
        with self.assertRaises(ValidationError):
            PhysicalDimensions(math.inf, ALEXA_265_HEIGHT_MM)  # infinite width
        with self.assertRaises(ValidationError):
            PhysicalDimensions(ALEXA_265_WIDTH_MM, -sys.float_info.min)  # negative height
        with self.assertRaises(ValidationError):
            PhysicalDimensions(ALEXA_265_WIDTH_MM, 0)  # zero height
        with self.assertRaises(ValidationError):
            PhysicalDimensions(ALEXA_265_WIDTH_MM, math.inf)  # infinite height
        #
        # test for compatibility with tagged camdkit 0.9
        #
        # Hmmm. You can't call .validate() if you can't construct the object
        #   self.assertFalse(PhysicalDimensions.validate(faux_dims))
        #
        # verify correct conversion to json
        json_from_instance: dict[str, Any] = PhysicalDimensions.to_json(d)
        self.assertDictEqual({'width': RED_V_RAPTOR_XL_8K_VV_WIDTH_MM,
                              'height': RED_V_RAPTOR_XL_8K_VV_HEIGHT_MM},
                             json_from_instance)
        # verify correct construction from json
        instance_from_json: PhysicalDimensions = PhysicalDimensions.from_json(json_from_instance)
        self.assertEqual(d, instance_from_json)
        expected_schema = {
            "properties": {
                "width": {
                    "exclusiveMinimum": 0.0,
                    "title": "Width",
                    "type": "number"
                },
                "height": {
                    "exclusiveMinimum": 0.0,
                    "title": "Height",
                    "type": "number"
                }
            },
            "required": [
                "width",
                "height"
            ],
            "title": "PhysicalDimensions",
            "type": "object"
        }
        schema = PhysicalDimensions.make_json_schema()
        self.assertDictEqual(expected_schema, schema)

    def test_sensel_dimensions(self):
        with self.assertRaises(TypeError):
            SenselDimensions()
        d = SenselDimensions(ALEXA_265_WIDTH_PX, ALEXA_265_HEIGHT_PX)
        self.assertEqual(ALEXA_265_WIDTH_PX, d.width)
        self.assertEqual(ALEXA_265_HEIGHT_PX, d.height)
        d.width = RED_V_RAPTOR_XL_8K_VV_WIDTH_PX
        d.height = RED_V_RAPTOR_XL_8K_VV_HEIGHT_PX
        self.assertEqual(RED_V_RAPTOR_XL_8K_VV_HEIGHT_PX, d.height)
        self.assertEqual(RED_V_RAPTOR_XL_8K_VV_WIDTH_PX, d.width)
        with self.assertRaises(ValidationError):
            SenselDimensions(ALEXA_YMCA_WIDTH_PX, 1)  # width type error
        with self.assertRaises(ValidationError):
            SenselDimensions(1, ALEXA_YMCA_HEIGHT_MM)  # height type error
        with self.assertRaises(ValidationError):
            SenselDimensions(-1, ALEXA_265_HEIGHT_MM)  # negative width
        with self.assertRaises(ValidationError):
            SenselDimensions(0, ALEXA_265_HEIGHT_MM)  # zero width
        with self.assertRaises(ValidationError):
            SenselDimensions(math.inf, ALEXA_265_HEIGHT_MM)  # infinite width
        with self.assertRaises(ValidationError):
            SenselDimensions(ALEXA_265_WIDTH_MM, -1)  # negative height
        with self.assertRaises(ValidationError):
            SenselDimensions(ALEXA_265_WIDTH_MM, 0)  # zero height
        with self.assertRaises(ValidationError):
            SenselDimensions(ALEXA_265_WIDTH_MM, math.inf)  # infinite height
        SenselDimensions.validate(d)
        expected_json = {'width': RED_V_RAPTOR_XL_8K_VV_WIDTH_PX,
                         'height': RED_V_RAPTOR_XL_8K_VV_HEIGHT_PX }
        json_from_instance: dict[str, Any] = SenselDimensions.to_json(d)
        self.assertDictEqual(expected_json, json_from_instance)
        instance_from_json: SenselDimensions = SenselDimensions.from_json(json_from_instance)
        self.assertEqual(d, instance_from_json)
        expected_schema = {
            "properties": {
                "width": {
                    "exclusiveMinimum": 0,
                    "title": "Width",
                    "type": "integer"
                },
                "height": {
                    "exclusiveMinimum": 0.0,
                    "title": "Height",
                    "type": "number"
                }
            },
            "required": [
                "width",
                "height"
            ],
            "title": "SenselDimensions",
            "type": "object"
        }
        schema = SenselDimensions.make_json_schema()
        self.assertDictEqual(expected_schema, schema)

    def test_shutter_angle(self):
        with self.assertRaises(TypeError):
            ShutterAngle()
        s = ShutterAngle(THIRTY_DEGREES)
        self.assertEqual(THIRTY_DEGREES, s.angle)
        s.angle = SIXTY_DEGREES
        self.assertEqual(SIXTY_DEGREES, s.angle)
        with self.assertRaises(ValidationError):
            ShutterAngle(0.0 + 0.0j)
        with self.assertRaises(ValidationError):
            ShutterAngle(-sys.float_info.min)
        with self.assertRaises(ValidationError):
            ShutterAngle(0.0)
        s.angle = THREE_HUNDRED_SIXTY_DEGREES
        with self.assertRaises(ValidationError):
            ShutterAngle(THREE_HUNDRED_SIXTY_DEGREES + 1)
            # What Pierre warned us about: this passes validation
            # ShutterAngle(THREE_HUNDRED_SIXTY_DEGREES + sys.float_info.min)
        ShutterAngle.validate(ShutterAngle(THIRTY_DEGREES))
        json_from_instance: dict[str, Any] = ShutterAngle.to_json(s)
        self.assertDictEqual({'angle': THREE_HUNDRED_SIXTY_DEGREES},
                             json_from_instance)
        instance_from_json: ShutterAngle = ShutterAngle.from_json(json_from_instance)
        self.assertEqual(s, instance_from_json)
        expected_schema = {
            "exclusiveMinimum": 0.0,
            "maximum": 360.0,
            "type": "number"
        }
        schema = ShutterAngle.make_json_schema()
        self.assertDictEqual(expected_schema, schema)

    def test_static_camera(self):
        sc = StaticCamera()

        self.assertIsNone(sc.capture_frame_rate)
        with self.assertRaises(ValidationError):
            sc.capture_frame_rate = 1+2j
        valid_capture_frame_rate = StrictlyPositiveRational(30, 1)
        sc.capture_frame_rate = valid_capture_frame_rate
        self.assertEqual(valid_capture_frame_rate, sc.capture_frame_rate)

        self.assertIsNone(sc.active_sensor_physical_dimensions)
        with self.assertRaises(ValidationError):
            sc.active_sensor_physical_dimensions = PhysicalDimensions(-1.0, 1.0)
        valid_active_sensor_physical_dimensions = PhysicalDimensions(ALEXA_265_WIDTH_MM,
                                                                     ALEXA_265_HEIGHT_MM)
        sc.active_sensor_physical_dimensions = valid_active_sensor_physical_dimensions
        self.assertEqual(valid_active_sensor_physical_dimensions, sc.active_sensor_physical_dimensions)

        self.assertIsNone(sc.active_sensor_resolution)
        with self.assertRaises(ValidationError):
            sc.active_sensor_resolution = SenselDimensions(-1, 1)
        valid_active_sensor_resolution = SenselDimensions(ALEXA_265_WIDTH_PX,
                                                                     ALEXA_265_HEIGHT_PX)
        sc.active_sensor_resolution = valid_active_sensor_resolution
        self.assertEqual(valid_active_sensor_resolution, sc.active_sensor_resolution)

        self.assertIsNone(sc.make)
        with self.assertRaises(ValidationError):
            sc.make = 0+0.1j
        valid_make = "aaton"
        sc.make = valid_make
        self.assertEqual(valid_make, sc.make)

        self.assertIsNone(sc.model_name)
        with self.assertRaises(ValidationError):
            sc.model_name = 1
        valid_model = "delta penelope"
        sc.model_name = valid_model
        self.assertEqual(valid_model, sc.model_name)

        self.assertIsNone(sc.serial_number)
        with self.assertRaises(ValidationError):
            sc.serial_number = 1
        valid_serial_number = "s/n 1 099 162"
        sc.serial_number = valid_serial_number
        self.assertEqual(valid_serial_number, sc.serial_number)

        self.assertIsNone(sc.firmware_version)
        with self.assertRaises(ValidationError):
            sc.firmware_version = 1
        valid_firmware_version = "SUP 3.0"
        sc.firmware_version = valid_firmware_version
        self.assertEqual(valid_firmware_version, sc.firmware_version)

        self.assertIsNone(sc.anamorphic_squeeze)
        with self.assertRaises(ValidationError):
            sc.anamorphic_squeeze = 1
        valid_anamorphic_squeeze = StrictlyPositiveRational(4, 3)
        sc.anamorphic_squeeze = valid_anamorphic_squeeze
        self.assertEqual(valid_anamorphic_squeeze, sc.anamorphic_squeeze)

        # self.assertIsNone(sc.iso)
        # with self.assertRaises(ValidationError):
        #     sc.iso = 800.5
        # valid_iso = 800
        # sc.iso = valid_iso
        # self.assertEqual(valid_iso, sc.iso)


        self.assertIsNone(sc.label)
        self.assertIsNone(sc.fdl_link)
        self.assertIsNone(sc.shutter_angle)
        print(json.dumps(sc.make_json_schema(), indent=2))

if __name__ == '__main__':
    unittest.main()
