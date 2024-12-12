#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Tests for clips"""

import unittest

from fractions import Fraction

from pydantic import ValidationError
from camdkit.numeric_types import Rational, StrictlyPositiveRational
from camdkit.string_types import NonBlankUTF8String
from camdkit.model_types import (FrameRate,
                                 SynchronizationSource, SynchronizationOffsets,
                                 SynchronizationPTP, Synchronization)
from camdkit.camera_types import PhysicalDimensions, SenselDimensions
from camdkit.clip import Clip

VALID_SAMPLE_ID = 'urn:uuid:abcdefab-abcd-abcd-abcd-abcdefabcdef'  # 8-4-4-4-12

class ClipTestCases(unittest.TestCase):
    pass

    # def test_frame_rate_validation(self):
    #     rate = FrameRate(24000, 1001)
    #     self.assertEqual(24000, rate.numerator)
    #     self.assertEqual(1001, rate.denominator)
    #     with self.assertRaises(ValidationError):
    #         FrameRate(-24000, 1001)

    def test_statics(self):
        active_sensor_physical_dimensions = PhysicalDimensions(width=36.0, height=24.0)
        active_sensor_resolution = SenselDimensions(width=3840, height=2160)
        anamorphic_squeeze = StrictlyPositiveRational(2, 1)  # needs to allow Fraction
        capture_frame_rate = StrictlyPositiveRational(24000, 1001)  # needs to allow Fraction
        camera_make = "Bob"
        camera_model = "Hello"
        camera_serial_number = "123456"
        camera_firmware = "7.1"
        camera_label = "A"
        iso = 13
        fdl_link = "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
        shutter_angle = 180

        clip = Clip()
        # camera static stuff first
        self.assertIsNone(clip.active_sensor_physical_dimensions)
        clip.active_sensor_physical_dimensions = active_sensor_physical_dimensions
        self.assertEqual(active_sensor_physical_dimensions, clip.active_sensor_physical_dimensions)
        self.assertIsNone(clip.active_sensor_resolution)
        clip.active_sensor_resolution = active_sensor_resolution
        self.assertEqual(active_sensor_resolution, clip.active_sensor_resolution)
        self.assertIsNone(clip.anamorphic_squeeze)
        clip.anamorphic_squeeze = anamorphic_squeeze
        self.assertEqual(anamorphic_squeeze, clip.anamorphic_squeeze)
        self.assertIsNone(clip.capture_frame_rate)
        clip.capture_frame_rate = capture_frame_rate
        self.assertEqual(capture_frame_rate, clip.capture_frame_rate)
        self.assertIsNone(clip.camera_make)
        clip.camera_make = camera_make
        self.assertEqual(camera_make, clip.camera_make)
        self.assertIsNone(clip.camera_model)
        clip.camera_model = camera_model
        self.assertEqual(camera_model, clip.camera_model)
        self.assertIsNone(clip.camera_serial_number)
        clip.camera_serial_number = camera_serial_number
        self.assertEqual(camera_serial_number, clip.camera_serial_number)
        self.assertIsNone(clip.camera_firmware)
        clip.camera_firmware = camera_firmware
        self.assertEqual(camera_firmware, clip.camera_firmware)
        self.assertIsNone(clip.camera_label)
        clip.camera_label = camera_label
        self.assertEqual(camera_label, clip.camera_label)
        self.assertIsNone(clip.iso)
        clip.iso = iso
        self.assertEqual(iso, clip.iso)
        self.assertIsNone(clip.fdl_link)
        clip.fdl_link = fdl_link
        self.assertEqual(fdl_link, clip.fdl_link)
        self.assertIsNone(clip.shutter_angle)
        clip.shutter_angle = shutter_angle
        self.assertEqual(shutter_angle, clip.shutter_angle)

        d = clip.to_json()
        print("now look at clip.to_json()")

    #     self.assertEqual(camera_make, clip.camera_make)  # add assertion here
    #     print(clip.model_dump_json(indent=2))
    #     # schema: dict[str, Any] = Clip.model_json_schema()
    #     # print(json.dumps(schema, indent=2))

    # def test_old_style(self):
    #     sync = Synchronization(
    #         locked=True,
    #         source=SynchronizationSource.PTP,
    #         frequency=StrictlyPositiveRational(24000, 1001),
    #         offsets=SynchronizationOffsets(1.0,2.0,3.0),
    #         present=True,
    #         ptp=SynchronizationPTP(1,"00:11:22:33:44:55",0.0)
    #     )
    #     c = Clip()
    #     c.timing_synchronization = sync
    #     self.assertEqual(True, c.timing_synchronization.locked)


if __name__ == '__main__':
    unittest.main()
