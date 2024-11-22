from typing import Optional
import unittest
import json

from pydantic import TypeAdapter, BaseModel, ValidationError
from camdkit.base_types import Rational, StrictlyPositiveRational, NonBlankUTF8String, SampleId, FrameRate
from camdkit.clip import Clip

VALID_SAMPLE_ID = 'urn:uuid:abcdefab-abcd-abcd-abcd-abcdefabcdef'  # 8-4-4-4-12

class ClipTestCases(unittest.TestCase):


    def test_frame_rate_validation(self):
        rate = FrameRate(24000, 1001)
        self.assertEqual(24000, rate.numerator)
        self.assertEqual(1001, rate.denominator)
        with self.assertRaises(ValidationError):
            FrameRate(-24000, 1001)

    def test_sampleID_validation(self):

        class Harness(BaseModel):
            id: Optional[SampleId] = None
        # check default value is None
        self.assertIsNone(Harness().id)
        # wrong type assigned
        with self.assertRaises(ValidationError):
            Harness(id=1)
        # correct type assigned, but noncomformant value
        with self.assertRaises(ValidationError):
            Harness(id='a noncomformant string')
        # try a conformant value during construction
        h0 = Harness(id=VALID_SAMPLE_ID)
        self.assertEqual(VALID_SAMPLE_ID, h0.id)
        # try a conformant string on RHS of assignment
        h1 = Harness()
        h1.id = VALID_SAMPLE_ID
        self.assertEqual(VALID_SAMPLE_ID, h1.id)

    def test_sample_id_to_json(self):
        class Harness(BaseModel):
            id: Optional[SampleId] = None
        kwargs = {'id': VALID_SAMPLE_ID}
        h = Harness(**kwargs)
        self.assertDictEqual(kwargs,
                             json.loads(Harness.model_dump_json(h)))

    def test_sample_from_json(self):
        class Harness(BaseModel):
            id: Optional[SampleId] = None
        kwargs = {'id': VALID_SAMPLE_ID}
        h0 = Harness(**kwargs)
        json_h = h0.model_dump()
        h1 = Harness(**json_h)
        self.assertEqual(h0, h1)





    def test_basic(self):
        # TODO figure out how to automatically promote (with checking!) str to NonBlankUTF8String
        #   both in the Clip ctor call, and in the assertEqual call
        camera_make = NonBlankUTF8String('ARRI')
        entrance_pupil_offset = Rational(80_000, 1)  # microns, so 8cm in front of image plane
        capture_fps = FrameRate(24, 1001)
        clip = Clip(SampleId('urn:uuid:abcdefab-abcd-abcd-abcd-abcdefabcdef'),
                    camera_make=camera_make,
                    entrance_pupil_offset=entrance_pupil_offset,
                    capture_fps=capture_fps)
        self.assertEqual(camera_make, clip.camera_make)  # add assertion here
        print(clip.model_dump_json(indent=2))
        # schema: dict[str, Any] = Clip.model_json_schema()
        # print(json.dumps(schema, indent=2))


if __name__ == '__main__':
    unittest.main()
