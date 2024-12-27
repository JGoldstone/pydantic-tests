import json
import unittest
from camdkit.model import *


class SchemaAccuracyTestCases(unittest.TestCase):
    def test_camera_make_non_handling(self):
        schema = Clip.make_json_schema()
        static_camera_properties = schema["properties"]["static"]["properties"]["camera"]
        camera_schema = static_camera_properties  # ["make"]
        for parameter in ("activeSensorPhysicalDimensions", "activeSensorResolution",
                          "captureFrameRate", "anamorphicSqueeze",
                          "label", "model", "serialNumber", "firmwareVersion",
                          "fdlLink", "isoSpeed", "shutterAngle"):
            del camera_schema["properties"][parameter]
        print(f"\nand the (trimmed-down) camera schema is:\n\n{json.dumps(camera_schema, indent=2)}")
        clip = Clip()
        self.assertIsNone(clip.camera_make)  # initial value is None, which the schema doesn't allow
        clip.camera_make = "apple"
        self.assertEqual("apple", clip.camera_make)  # reads back OK
        clip.camera_make = None
        self.assertIsNone(clip.camera_make)  # can be reset to None, which the schema doesn't allow
        # these are handed correctly
        for invalid_non_none_value in (0, 1.0, 0+2j, ("thomson",), {"vendor": "aaton"}, {"dalsa"}):
            with self.assertRaises(ValueError):
                clip.camera_make = invalid_non_none_value


if __name__ == '__main__':
    unittest.main()
