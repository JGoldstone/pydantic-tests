import sys
import math
import unittest
import json
from typing import Any, Optional, Annotated
from fractions import Fraction
from uuid import uuid4

from pydantic import ValidationError, BaseModel, Field

from camdkit.model_types import (PhysicalDimensions,
                                 ShutterAngle,
                                 SampleId,_SAMPLE_ID_RE_PATTERN, FrameRate,
                                 SynchronizationSource, SynchronizationOffsets,
                                 Synchronization, SynchronizationPTP)

ALEXA_265_WIDTH: float = 54.12  # mm
ALEXA_265_HEIGHT = 25.58  # mm
ALEXA_YMCA_WIDTH = 65 + 4.9e-6j  # inside-joke sensor from c. 2015; faux-Foveon depth
ALEXA_YMCA_HEIGHT = ALEXA_YMCA_WIDTH * Fraction(1, Fraction(276, 100))  # Ultra Panavision 70
RED_V_RAPTOR_XL_8K_VV_WIDTH = 40.96  # mm
RED_V_RAPTOR_XL_8K_VV_HEIGHT = 21.60  # mm

THIRTY_DEGREES = 30.0
SIXTY_DEGREES = 60.0
THREE_HUNDRED_SIXTY_DEGREES = 360.0

VALID_SAMPLE_ID_URN_0 = "urn:uuid:5ca5f233-11b5-4f43-8815-948d73e48a33"
VALID_SAMPLE_ID_URN_1 = "urn:uuid:5ca5f233-11b5-dead-beef-948d73e48a33"


class ModelTestCases(unittest.TestCase):

    # example of testing a struct:
    #   verify no-arg instantiation fails
    #   verify correct instantiation returns an object the attributes of which meet expectations
    #   verify one can set the object's attributes to new values
    #   verify trying to instantiate with arguments of invalid type raises a validation error
    #   when applicable, verify that trying to instantiate with arguments of the correct type
    #     but out-of-range or otherwise invalid values fail
    def test_physical_dimensions(self):
        with self.assertRaises(TypeError):
            PhysicalDimensions()  # no no-arg __init__() method
        d = PhysicalDimensions(ALEXA_265_WIDTH, ALEXA_265_HEIGHT)
        self.assertEqual(ALEXA_265_WIDTH, d.width)
        self.assertEqual(ALEXA_265_HEIGHT, d.height)
        d.width = RED_V_RAPTOR_XL_8K_VV_WIDTH
        d.height = RED_V_RAPTOR_XL_8K_VV_HEIGHT
        self.assertEqual(RED_V_RAPTOR_XL_8K_VV_WIDTH, d.width)
        self.assertEqual(RED_V_RAPTOR_XL_8K_VV_HEIGHT, d.height)
        # Test all the guardrails individually
        with self.assertRaises(ValidationError):
            PhysicalDimensions(ALEXA_YMCA_WIDTH, 1.0)  # width type error
        with self.assertRaises(ValidationError):
            PhysicalDimensions(1.0, ALEXA_YMCA_HEIGHT)  # height type error
        with self.assertRaises(ValidationError):
            PhysicalDimensions(-sys.float_info.min, ALEXA_265_HEIGHT)  # negative width
        with self.assertRaises(ValidationError):
            PhysicalDimensions(0, ALEXA_265_HEIGHT)  # zero width
        with self.assertRaises(ValidationError):
            PhysicalDimensions(math.inf, ALEXA_265_HEIGHT)  # infinite width
        with self.assertRaises(ValidationError):
            PhysicalDimensions(ALEXA_265_WIDTH, -sys.float_info.min)  # negative height
        with self.assertRaises(ValidationError):
            PhysicalDimensions(ALEXA_265_WIDTH, 0)  # zero height
        with self.assertRaises(ValidationError):
            PhysicalDimensions(ALEXA_265_WIDTH, math.inf)  # infinite height
        #
        # test for compatibility with tagged camdkit 0.9
        #
        # Hmmm. You can't call .validate() if you can't construct the object
        #   self.assertFalse(PhysicalDimensions.validate(faux_dims))
        #
        # verify correct conversion to json
        json_from_instance: dict[str, Any] = PhysicalDimensions.to_json(d)
        self.assertDictEqual({'width': RED_V_RAPTOR_XL_8K_VV_WIDTH,
                              'height': RED_V_RAPTOR_XL_8K_VV_HEIGHT},
                             json_from_instance)
        # verify correct construction from json
        instance_from_json: PhysicalDimensions = PhysicalDimensions.from_json(json_from_instance)
        self.assertEqual(d, instance_from_json)
        # verify introspected schema matches expectations
        schema = PhysicalDimensions.make_json_schema()
        print(json.dumps(schema, indent=2))


    # example of testing a scalar


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


    def test_sample_id(self):
        with self.assertRaises(TypeError):
            SampleId()
        s = SampleId(VALID_SAMPLE_ID_URN_0)
        self.assertEqual(VALID_SAMPLE_ID_URN_0, s.sample_id)
        s.sample_id = VALID_SAMPLE_ID_URN_1
        self.assertEqual(VALID_SAMPLE_ID_URN_1, s.sample_id)
        with self.assertRaises(ValidationError):
            SampleId('')
        with self.assertRaises(ValidationError):
            SampleId('fail')
        SampleId.validate(SampleId(VALID_SAMPLE_ID_URN_0))
        json_from_instance: dict[str, Any] = SampleId.to_json(s)
        self.assertDictEqual({'sampleId': VALID_SAMPLE_ID_URN_1},
                             json_from_instance)
        instance_from_json: SampleId = SampleId.from_json(json_from_instance)
        self.assertEqual(s, instance_from_json)
        schema = SampleId.make_json_schema()
        print(json.dumps(schema, indent=2))

    def test_synchronization_source_validation(self) -> None:
        # not perfect but better than nothing
        # TODO use changes in snake case to insert underscores
        self.assertListEqual([m.name.lower().replace('_','')
                              for m in SynchronizationSource],
                             [m.value.lower().replace('_','')
                              for m in SynchronizationSource])

    def test_synchronization_offsets_validation(self) -> None:
        with self.assertRaises(ValidationError):
            SynchronizationOffsets(translation='a', rotation=2.0, lens_encoders=3.0)


if __name__ == '__main__':
    unittest.main()
