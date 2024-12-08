from typing import Optional
import unittest
import json

from pydantic import TypeAdapter, BaseModel, ValidationError
from camdkit.base_types import Rational, StrictlyPositiveRational, NonBlankUTF8String
from camdkit.model_types import (SampleId, FrameRate,
                                 SynchronizationSource, SynchronizationOffsets,
                                 SynchronizationPTP, Synchronization, PhysicalDimensions)
from camdkit.clip import Clip

VALID_SAMPLE_ID = 'urn:uuid:abcdefab-abcd-abcd-abcd-abcdefabcdef'  # 8-4-4-4-12

class ClipTestCases(unittest.TestCase):


    def test_frame_rate_validation(self):
        rate = FrameRate(24000, 1001)
        self.assertEqual(24000, rate.numerator)
        self.assertEqual(1001, rate.denominator)
        with self.assertRaises(ValidationError):
            FrameRate(-24000, 1001)

    def test_basic(self):
        camera_make = NonBlankUTF8String('ARRI')
        entrance_pupil_offset = Rational(80_000, 1)  # microns, so 8cm in front of image plane
        # capture_fps = FrameRate(24, 1001)
        clip = Clip()
        clip.camera_make = camera_make
        self.assertEqual(camera_make, clip.camera_make)  # add assertion here
        print(clip.model_dump_json(indent=2))
        # schema: dict[str, Any] = Clip.model_json_schema()
        # print(json.dumps(schema, indent=2))

    def test_old_style(self):
        sync = Synchronization(
            locked=True,
            source=SynchronizationSource.PTP,
            frequency=StrictlyPositiveRational(24000, 1001),
            offsets=SynchronizationOffsets(1.0,2.0,3.0),
            present=True,
            ptp=SynchronizationPTP(1,"00:11:22:33:44:55",0.0)
        )
        c = Clip()
        c.timing_synchronization = sync
        self.assertEqual(True, c.timing_synchronization.locked)


if __name__ == '__main__':
    unittest.main()
