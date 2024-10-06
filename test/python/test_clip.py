import unittest

from camdkit.types import Rational, StrictlyPositiveRational, NonBlankUTF8String
from camdkit.clip import Clip

class ClipTestCases(unittest.TestCase):
    def test_basic(self):
        camera_make = NonBlankUTF8String('ARRI')
        entrance_pupil_offset = Rational(80_000, 1)  # microns, so 8cm in front of image plane
        capture_fps = StrictlyPositiveRational(24, 1001)
        clip = Clip(camera_make=camera_make,
                    entrance_pupil_offset=entrance_pupil_offset,
                    capture_fps=capture_fps)
        self.assertEqual(camera_make, clip.camera_make)  # add assertion here
        print(clip.model_dump_json())


if __name__ == '__main__':
    unittest.main()
