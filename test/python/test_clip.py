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
        # reference static camera values
        capture_frame_rate = Fraction(24000, 1001)
        canonical_capture_frame_rate = StrictlyPositiveRational(24000, 1001)
        active_sensor_physical_dimensions = PhysicalDimensions(width=36.0, height=24.0)
        active_sensor_resolution = SenselDimensions(width=3840, height=2160)
        anamorphic_squeeze = Fraction(2, 1)
        canonical_anamorphic_squeeze = StrictlyPositiveRational(2, 1)
        camera_make = "Bob"
        camera_model = "Hello"
        camera_serial_number = "123456"
        camera_firmware = "7.1"
        camera_label = "A"
        iso = 13
        fdl_link = "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
        shutter_angle = 180

        # reference static lens values
        lens_distortion_overscan_max = 1.2
        lens_undistortion_overscan_max = 1.2
        lens_make = "ABC"
        lens_model = "FGH"
        lens_firmware = "1-dev.1"
        lens_serial_number = "123456789"
        lens_nominal_focal_length = 24
        lens_distortion_overscan = (1.0, 1.0)

        clip = Clip()
        self.assertIsNone(clip.active_sensor_physical_dimensions)
        clip.active_sensor_physical_dimensions = active_sensor_physical_dimensions
        self.assertEqual(active_sensor_physical_dimensions, clip.active_sensor_physical_dimensions)
        self.assertIsNone(clip.active_sensor_resolution)
        clip.active_sensor_resolution = active_sensor_resolution
        self.assertEqual(active_sensor_resolution, clip.active_sensor_resolution)
        self.assertIsNone(clip.anamorphic_squeeze)
        clip.anamorphic_squeeze = anamorphic_squeeze
        self.assertEqual(canonical_anamorphic_squeeze, clip.anamorphic_squeeze)
        self.assertIsNone(clip.capture_frame_rate)
        clip.capture_frame_rate = capture_frame_rate
        self.assertEqual(canonical_capture_frame_rate, clip.capture_frame_rate)
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

        # lens static stuff next
        self.assertIsNone(clip.lens_distortion_overscan_max)
        clip.lens_distortion_overscan_max = lens_distortion_overscan_max
        self.assertEqual(lens_distortion_overscan_max, clip.lens_distortion_overscan_max)
        self.assertIsNone(clip.lens_undistortion_overscan_max)
        clip.lens_undistortion_overscan_max = lens_undistortion_overscan_max
        self.assertEqual(lens_undistortion_overscan_max, clip.lens_undistortion_overscan_max)
        self.assertIsNone(clip.lens_make)
        clip.lens_make = lens_make
        self.assertEqual(lens_make, clip.lens_make)
        self.assertIsNone(clip.lens_model)
        clip.lens_model = lens_model
        self.assertEqual(lens_model, clip.lens_model)
        self.assertIsNone(clip.lens_firmware)
        clip.lens_firmware = lens_firmware
        self.assertEqual(lens_firmware, clip.lens_firmware)
        self.assertIsNone(clip.lens_serial_number)
        clip.lens_serial_number = lens_serial_number
        self.assertEqual(lens_serial_number, clip.lens_serial_number)
        self.assertIsNone(clip.lens_nominal_focal_length)
        clip.lens_nominal_focal_length = lens_nominal_focal_length

        # lens dynamic stuff
        self.assertIsNone(clip.lens_distortion_overscan)
        clip.lens_distortion_overscan = lens_distortion_overscan
        self.assertEqual(lens_distortion_overscan, clip.lens_distortion_overscan)



        d = clip.to_json()
        self.assertEqual(d["static"]["camera"]["captureFrameRate"], {"num": 24000, "denom": 1001})
        self.assertDictEqual(d["static"]["camera"]["activeSensorPhysicalDimensions"], {"height": 24.0, "width": 36.0})
        self.assertDictEqual(d["static"]["camera"]["activeSensorResolution"], {"height": 2160, "width": 3840})
        self.assertEqual(d["static"]["camera"]["make"], camera_make)
        self.assertEqual(d["static"]["camera"]["model"], camera_model)
        self.assertEqual(d["static"]["camera"]["serialNumber"], camera_serial_number)
        self.assertEqual(d["static"]["camera"]["firmwareVersion"], "7.1")
        self.assertEqual(d["static"]["camera"]["label"], "A")

        self.assertEqual(d["static"]["lens"]["distortionOverscanMax"], 1.2)
        self.assertEqual(d["static"]["lens"]["undistortionOverscanMax"], 1.2)
        self.assertEqual(d["static"]["lens"]["make"], "ABC")
        self.assertEqual(d["static"]["lens"]["model"], "FGH")
        self.assertEqual(d["static"]["lens"]["serialNumber"], "123456789")
        self.assertEqual(d["static"]["lens"]["firmwareVersion"], "1-dev.1")
        self.assertEqual(d["static"]["lens"]["nominalFocalLength"], 24)

        self.assertTupleEqual(d["lens"]["distortionOverscan"], (1.0, 1.0))

        rt: Clip = Clip.from_json(d)
        self.assertEqual(clip, rt)

    def test_lens_regular_parameters(self):
        # reference values
        lens_distortion_overscan = (1.0, 1.0)

        clip = Clip()
        self.assertIsNone(clip.lens_distortion_overscan)
        clip.lens_distortion_overscan = lens_distortion_overscan
        self.assertEqual(lens_distortion_overscan, clip.lens_distortion_overscan)

        clip_as_json = clip.to_json()
        self.assertTupleEqual(clip_as_json["lens"]["distortionOverscan"], (1.0, 1.0))

        clip_from_json: Clip = Clip.from_json(clip_as_json)
        self.assertEqual(clip, clip_from_json)



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
