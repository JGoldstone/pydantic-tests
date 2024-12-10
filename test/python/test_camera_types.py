import sys
import math
import unittest
import json

from typing import Any
from fractions import Fraction

from pydantic import ValidationError

from camdkit.camera_types import (PhysicalDimensions, ShutterAngle, SenselDimensions)

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
        # verify introspected schema matches expectations
        schema = PhysicalDimensions.make_json_schema()
        print(json.dumps(schema, indent=2))

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
        schema = ShutterAngle.make_json_schema()
        print(json.dumps(schema, indent=2))

if __name__ == '__main__':
    unittest.main()
