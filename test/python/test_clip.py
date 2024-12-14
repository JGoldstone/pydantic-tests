#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Tests for clips"""

import unittest

from fractions import Fraction

from pydantic import ValidationError
from pydantic.v1 import NonNegativeFloat

from camdkit.lens_types import (ExposureFalloff,
                                Distortion, DistortionOffset, ProjectionOffset,
                                FizEncoders, RawFizEncoders)
from camdkit.numeric_types import Rational, StrictlyPositiveRational, NonNegativeFloat, NonNegativeInt
from camdkit.string_types import NonBlankUTF8String
from camdkit.camera_types import PhysicalDimensions, SenselDimensions
from camdkit.timing_types import Timestamp, Timecode, TimecodeFormat, FrameRate, SynchronizationSource, \
    SynchronizationOffsets, SynchronizationPTP, Synchronization
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
        lens_t_number = (2000, 4000)
        lens_f_number = (1200, 2800)
        lens_focal_length = (2.0, 4.0)
        lens_focus_distance = (2, 4)
        lens_entrance_pupil_offset = (1.23, 2.34)
        lens_encoders = (FizEncoders(focus=0.1, iris=0.2, zoom=0.3),
                         FizEncoders(focus=0.1, iris=0.2, zoom=0.3))
        lens_raw_encoders = (RawFizEncoders(focus=1, iris=2, zoom=3),
                             RawFizEncoders(focus=1, iris=2, zoom=3))
        lens_distortion_overscan = (1.0, 1.0)
        lens_undistortion_overscan = (1.0, 1.0)
        lens_exposure_falloff = (ExposureFalloff(1.0, 2.0, 3.0),
                                 ExposureFalloff(1.0, 2.0, 3.0))
        # These (copied from the current main camdkit) fail validation because the typing is for tuples, not lists
        # lens_distortion = (Distortion([1.0, 2.0, 3.0], [1.0, 2.0], "Brown-Conrady D-U"),
        #                    Distortion([1.0, 2.0, 3.0], [1.0, 2.0], "Brown-Conrady D-U"))
        # lens_undistortion = (Distortion([1.0, 2.0, 3.0], [1.0, 2.0], "Brown-Conrady U-D"),
        #                      Distortion([1.0, 2.0, 3.0], [1.0, 2.0], "Brown-Conrady U-D"))
        lens_distortion = (Distortion((1.0, 2.0, 3.0), (1.0, 2.0), "Brown-Conrady D-U"),
                           Distortion((1.0, 2.0, 3.0), (1.0, 2.0), "Brown-Conrady D-U"))
        lens_undistortion = (Distortion((1.0, 2.0, 3.0), (1.0, 2.0), "Brown-Conrady U-D"),
                             Distortion((1.0, 2.0, 3.0), (1.0, 2.0), "Brown-Conrady U-D"))
        lens_distortion_offset = (DistortionOffset(1.0, 2.0), DistortionOffset(1.0, 2.0))
        lens_projection_offset = (ProjectionOffset(0.1, 0.2), ProjectionOffset(0.1, 0.2))

        clip = Clip()
        self.assertIsNone(clip.lens_t_number)
        clip.lens_t_number = lens_t_number
        self.assertEqual(lens_t_number, clip.lens_t_number)
        self.assertIsNone(clip.lens_f_number)
        clip.lens_f_number = lens_f_number
        self.assertEqual(lens_f_number, clip.lens_f_number)
        self.assertIsNone(clip.lens_focal_length)
        clip.lens_focal_length = lens_focal_length
        self.assertEqual(lens_focal_length, clip.lens_focal_length)
        self.assertIsNone(clip.lens_focus_distance)
        clip.lens_focus_distance = lens_focus_distance
        self.assertEqual(lens_focus_distance, clip.lens_focus_distance)
        self.assertIsNone(clip.lens_entrance_pupil_offset)
        clip.lens_entrance_pupil_offset = lens_entrance_pupil_offset
        self.assertEqual(lens_entrance_pupil_offset, clip.lens_entrance_pupil_offset)
        self.assertIsNone(clip.lens_encoders)
        clip.lens_encoders = lens_encoders
        self.assertEqual(lens_encoders, clip.lens_encoders)
        self.assertIsNone(clip.lens_raw_encoders)
        clip.lens_raw_encoders = lens_raw_encoders
        self.assertEqual(lens_raw_encoders, clip.lens_raw_encoders)
        self.assertIsNone(clip.lens_distortion_overscan)
        clip.lens_distortion_overscan = lens_distortion_overscan
        self.assertEqual(lens_distortion_overscan, clip.lens_distortion_overscan)
        self.assertIsNone(clip.lens_undistortion_overscan)
        clip.lens_undistortion_overscan = lens_undistortion_overscan
        self.assertEqual(lens_undistortion_overscan, clip.lens_undistortion_overscan)
        self.assertIsNone(clip.lens_exposure_falloff)
        clip.lens_exposure_falloff = lens_exposure_falloff
        self.assertEqual(lens_exposure_falloff, clip.lens_exposure_falloff)
        self.assertIsNone(clip.lens_distortion)
        clip.lens_distortion = lens_distortion
        self.assertEqual(lens_distortion, clip.lens_distortion)
        self.assertIsNone(clip.lens_undistortion)
        clip.lens_undistortion = lens_undistortion
        self.assertEqual(lens_undistortion, clip.lens_undistortion)
        self.assertIsNone(clip.lens_distortion_offset)
        clip.lens_distortion_offset = lens_distortion_offset
        self.assertEqual(lens_distortion_offset, clip.lens_distortion_offset)
        self.assertIsNone(clip.lens_projection_offset)
        clip.lens_projection_offset = lens_projection_offset
        self.assertEqual(lens_projection_offset, clip.lens_projection_offset)
        
        clip_as_json = clip.to_json()
        # self.assertTupleEqual(clip_as_json["lens"]["custom"], lens_custom)
        self.assertTupleEqual(clip_as_json["lens"]["tStop"], lens_t_number)
        self.assertTupleEqual(clip_as_json["lens"]["fStop"], lens_f_number)
        self.assertTupleEqual(clip_as_json["lens"]["focalLength"], lens_focal_length)
        self.assertTupleEqual(clip_as_json["lens"]["focusDistance"], lens_focus_distance)
        self.assertTupleEqual(clip_as_json["lens"]["entrancePupilOffset"], lens_entrance_pupil_offset)
        self.assertTupleEqual(clip_as_json["lens"]["encoders"], ({ "focus":0.1, "iris":0.2, "zoom":0.3 },
                                                                 { "focus":0.1, "iris":0.2, "zoom":0.3 }))
        self.assertTupleEqual(clip_as_json["lens"]["rawEncoders"], ({ "focus":1, "iris":2, "zoom":3 },
                                                                    { "focus":1, "iris":2, "zoom":3 }))
        self.assertTupleEqual(clip_as_json["lens"]["distortionOverscan"], lens_distortion_overscan)
        self.assertTupleEqual(clip_as_json["lens"]["undistortionOverscan"], lens_undistortion_overscan)
        self.assertTupleEqual(clip_as_json["lens"]["exposureFalloff"], ({"a1": 1.0, "a2": 2.0, "a3": 3.0},
                                                             {"a1": 1.0, "a2": 2.0, "a3": 3.0}))
        self.assertTupleEqual(clip_as_json["lens"]["distortion"],
                              ({"radial": (1.0, 2.0, 3.0), "tangential": (1.0, 2.0), "model": "Brown-Conrady D-U"},
                               {"radial": (1.0, 2.0, 3.0), "tangential": (1.0, 2.0), "model": "Brown-Conrady D-U"}))
        self.assertTupleEqual(clip_as_json["lens"]["undistortion"],
                              ({"radial": (1.0, 2.0, 3.0), "tangential": (1.0, 2.0), "model": "Brown-Conrady U-D"},
                               {"radial": (1.0, 2.0, 3.0), "tangential": (1.0, 2.0), "model": "Brown-Conrady U-D"}))
        self.assertTupleEqual(clip_as_json["lens"]["distortionOffset"], ({"x": 1.0, "y": 2.0}, {"x": 1.0, "y": 2.0}))
        self.assertTupleEqual(clip_as_json["lens"]["projectionOffset"], ({"x": 0.1, "y": 0.2}, {"x": 0.1, "y": 0.2}))

        clip_from_json: Clip = Clip.from_json(clip_as_json)
        self.assertEqual(clip, clip_from_json)

    def test_timing_regular_parameters(self):
        # reference values
        timing_mode = ("internal", "internal")
        timing_sample_timestamp = (Timestamp(1718806554, 0),
                                    Timestamp(1718806555, 0))
        timing_recorded_timestamp = (Timestamp(1718806000, 0),
                                      Timestamp(1718806001, 0))
        timing_sequence_number = (0, 1)
        sample_rate = StrictlyPositiveRational(24000, 1001)
        timing_sample_rate = (sample_rate, sample_rate)
        timecode0 = Timecode(1, 2, 3, 4,
                            TimecodeFormat(StrictlyPositiveRational(24, 1),
                                           0))
        timecode1= Timecode(1, 2, 3, 5,
                            TimecodeFormat(StrictlyPositiveRational(24, 1),
                                           0))
        timing_timecode = (timecode0, timecode1)
        ptp = SynchronizationPTP(1, "00:11:22:33:44:55", 0.0)
        sync_offsets = SynchronizationOffsets(1.0, 2.0, 3.0)
        synchronization = Synchronization(present=True,
                                          locked=True,
                                          frequency=sample_rate,
                                          source=SynchronizationSource.PTP,
                                          ptp=ptp,
                                          offsets=sync_offsets)
        timing_synchronization = (synchronization, synchronization)

        clip = Clip()
        self.assertIsNone(clip.timing_mode)
        clip.timing_mode = timing_mode
        self.assertEqual(timing_mode, clip.timing_mode)
        self.assertIsNone(clip.timing_sample_timestamp)
        clip.timing_sample_timestamp = timing_sample_timestamp
        self.assertEqual(timing_sample_timestamp, clip.timing_sample_timestamp)
        self.assertIsNone(clip.timing_recorded_timestamp)
        clip.timing_recorded_timestamp = timing_recorded_timestamp
        self.assertEqual(timing_recorded_timestamp, clip.timing_recorded_timestamp)
        self.assertIsNone(clip.timing_sequence_number)
        clip.timing_sequence_number = timing_sequence_number
        self.assertEqual(timing_sequence_number, clip.timing_sequence_number)
        self.assertIsNone(clip.timing_sample_rate)
        clip.timing_sample_rate = timing_sample_rate
        self.assertEqual(timing_sample_rate, clip.timing_sample_rate)
        self.assertIsNone(clip.timing_timecode)
        clip.timing_timecode = timing_timecode
        self.assertEqual(timing_timecode, clip.timing_timecode)
        self.assertIsNone(clip.timing_synchronization)
        clip.timing_synchronization = timing_synchronization
        self.assertEqual(timing_synchronization, clip.timing_synchronization)

        clip_as_json = clip.to_json()
        self.assertTupleEqual(clip_as_json["timing"]["mode"], timing_mode)
        self.assertTupleEqual(clip_as_json["timing"]["sampleTimestamp"], (
            {"seconds": 1718806554, "nanoseconds": 0},
            {"seconds": 1718806555, "nanoseconds": 0}))
        self.assertTupleEqual(clip_as_json["timing"]["recordedTimestamp"], (
            { "seconds": 1718806000, "nanoseconds": 0 },
            { "seconds": 1718806001, "nanoseconds": 0 }))
        self.assertTupleEqual(clip_as_json["timing"]["sequenceNumber"], timing_sequence_number)
        self.assertTupleEqual(clip_as_json["timing"]["sampleRate"], (
            { "num": 24000, "denom": 1001 },
            { "num": 24000, "denom": 1001 }))
        self.assertTupleEqual(clip_as_json["timing"]["timecode"], (
            { "hours":1, "minutes":2, "seconds":3, "frames":4,
              "format": { "frameRate": { "num": 24, "denom": 1 },
                          "subFrame": 0 } },
            { "hours": 1,"minutes": 2,"seconds": 3,"frames": 5,
              "format": { "frameRate": { "num": 24, "denom": 1 },
                          "subFrame": 0 } }))
        expected_synchronization_dict = {
            "present": True, "locked": True,
            "frequency": {"num": 24000, "denom": 1001},
            "source": "ptp",
            "ptp": {"offset": 0.0, "domain": 1, "master": "00:11:22:33:44:55"},
            "offsets": {"translation": 1.0, "rotation": 2.0, "lensEncoders": 3.0}}
        self.assertTupleEqual(clip_as_json["timing"]["synchronization"],
                              (expected_synchronization_dict,
                               expected_synchronization_dict))
        clip_from_json: Clip = Clip.from_json(clip_as_json)
        self.assertEqual(clip, clip_from_json)

if __name__ == '__main__':
    unittest.main()
