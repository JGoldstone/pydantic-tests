#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types to model time, timing and synchronization"""

import json
import unittest

from pydantic import ValidationError
from rfc3339_validator import validate_rfc3339

from camdkit.numeric_types import (MAX_INT_8, MAX_UINT_32, MAX_UINT_48,
                                   Rational, StrictlyPositiveRational)
from camdkit.timing_types import (TimecodeFormat,
                                  Timecode,
                                  Timestamp,
                                  SynchronizationSource,
                                  SynchronizationOffsets,
                                  SynchronizationPTP,
                                  Synchronization)


class TimingTestCases(unittest.TestCase):

    def test_timecode_format(self):
        with self.assertRaises(ValidationError):
            TimecodeFormat(0, 0)
        with self.assertRaises(ValidationError):
            TimecodeFormat(Rational(-1, 1), 0)
        with self.assertRaises(ValidationError):
            TimecodeFormat(Rational(0, 1), 0)
        frame_rate_30fps_num = 30
        frame_rate_30fps_denom = 1
        frame_rate_30fps = StrictlyPositiveRational(frame_rate_30fps_num,
                                                    frame_rate_30fps_denom)
        sub_frame = 0
        tf = TimecodeFormat(frame_rate_30fps, sub_frame)
        self.assertEqual(tf.frame_rate, frame_rate_30fps)
        with self.assertRaises(ValidationError):
            tf.frame_rate = "foo"
        with self.assertRaises(ValidationError):
            tf.frame_rate = 29.976
        with self.assertRaises(ValidationError):
            tf.frame_rate = Rational(-1, 1)
        with self.assertRaises(ValidationError):
            TimecodeFormat(frame_rate_30fps, "foo")
        with self.assertRaises(ValidationError):
            TimecodeFormat(frame_rate_30fps, 1.0)

        timecode_format_as_json = TimecodeFormat.to_json(tf)
        self.assertEqual(timecode_format_as_json["frameRate"]["num"],
                         frame_rate_30fps_num)
        self.assertEqual(timecode_format_as_json["frameRate"]["denom"],
                         frame_rate_30fps_denom)
        self.assertEqual(timecode_format_as_json["subFrame"], sub_frame)

        timecode_format_from_json = TimecodeFormat.from_json(timecode_format_as_json)
        self.assertEqual(tf, timecode_format_from_json)

        expected_schema = {
            "type": "object",
            "description": "The timecode format is defined as a rational frame rate and - where a\nsignal with sub-frames is described, such as an interlaced signal - an\nindex of which sub-frame is referred to by the timecode.\n",
            "required": [
                "frameRate"
            ],
            "additionalProperties": False,
            "properties": {
                "frameRate": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "num",
                        "denom"
                    ],
                    "properties": {
                        "num": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 2147483647
                        },
                        "denom": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 4294967295
                        }
                    }
                },
                "subFrame": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 4294967295
                }
            }
        }
        actual_schema = tf.make_json_schema()
        self.assertEqual(expected_schema, actual_schema)

    def test_timecode(self):
        thirty_fps_num = 30
        thirty_fps_denom = 1
        sub_frame = 0
        valid_timecode_format = TimecodeFormat(StrictlyPositiveRational(thirty_fps_num, thirty_fps_denom), sub_frame)
        with self.assertRaises(ValidationError):
            Timecode("foo", 0, 0, 0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0.0, 0, 0, 0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(-1, 0, 0, 0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(24, 0, 0, 0, valid_timecode_format)
        tc = Timecode(0, 0, 0, 0, valid_timecode_format)
        self.assertEqual(0, tc.hours)
        tc = Timecode(23, 0, 0, 0, valid_timecode_format)
        self.assertEqual(23, tc.hours)
        with self.assertRaises(ValidationError):
            Timecode(0, "foo", 0, 0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0, 0.0, 0, 0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0, -1, 0, 0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0, 60, 0, 0, valid_timecode_format)
        tc = Timecode(0, 59, 0, 0, valid_timecode_format)
        self.assertEqual(59, tc.minutes)
        with self.assertRaises(ValidationError):
            Timecode(0, 0, "foo", 0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0, 0, 0.0, 0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0, 0, -1, 0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0, 0, 60, 0, valid_timecode_format)
        tc = Timecode(0, 0, 59, 0, valid_timecode_format)
        self.assertEqual(59, tc.seconds)
        with self.assertRaises(ValidationError):
            Timecode(0, 0, 0, "foo", valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0, 0, 0, 0.0, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0, 0, 0, -1, valid_timecode_format)
        with self.assertRaises(ValidationError):
            Timecode(0, 0, 0, thirty_fps_num, valid_timecode_format)
        tc = Timecode(0, 0, 0, thirty_fps_num - 1, valid_timecode_format)
        self.assertEqual(thirty_fps_num - 1, tc.frames)
        with self.assertRaises(ValidationError):
            Timecode(0, 0, 0, 0, "foo")

        valid_hours: int = 1
        valid_minutes: int = 2
        valid_seconds: int =  3
        valid_frames: int = 4
        tc = Timecode(valid_hours, valid_minutes, valid_seconds, valid_frames, valid_timecode_format)
        with self.assertRaises(ValidationError):
            tc.hours = "foo"
        with self.assertRaises(ValidationError):
            tc.hours = 0.0
        with self.assertRaises(ValidationError):
            tc.hours = -1
        with self.assertRaises(ValidationError):
            tc.hours = 24
        with self.assertRaises(ValidationError):
            tc.minutes = "foo"
        with self.assertRaises(ValidationError):
            tc.minutes = 0.0
        with self.assertRaises(ValidationError):
            tc.minutes = -1
        with self.assertRaises(ValidationError):
            tc.minutes = 60
        with self.assertRaises(ValidationError):
            tc.seconds = "foo"
        with self.assertRaises(ValidationError):
            tc.seconds = 0.0
        with self.assertRaises(ValidationError):
            tc.seconds = -1
        with self.assertRaises(ValidationError):
            tc.seconds = 60
        with self.assertRaises(ValidationError):
            tc.frames = "foo"
        with self.assertRaises(ValidationError):
            tc.frames = 0.0
        with self.assertRaises(ValidationError):
            tc.frames = -1
        with self.assertRaises(ValidationError):
            tc.frames = 120
        with self.assertRaises(ValidationError):
            tc.format = "foo"
        with self.assertRaises(ValidationError):
            tc.format = 0.0
        with self.assertRaises(ValidationError):
            tc.format = 0
        doubled_hours: int = valid_hours * 2
        doubled_minutes: int = valid_minutes * 2
        doubled_seconds: int = valid_seconds * 2
        doubled_frames: int = valid_frames * 2
        thirty_fps_drop_frame_format = TimecodeFormat(StrictlyPositiveRational(30000, 1001), 0)
        tc.hours = doubled_hours
        self.assertEqual(tc.hours, doubled_hours)
        tc.minutes = doubled_minutes
        self.assertEqual(tc.minutes, doubled_minutes)
        tc.seconds = doubled_seconds
        self.assertEqual(tc.seconds, doubled_seconds)
        tc.frames = doubled_frames
        self.assertEqual(tc.frames, doubled_frames)
        tc.format = thirty_fps_drop_frame_format
        self.assertEqual(tc.format, thirty_fps_drop_frame_format)

        timecode_as_json = Timecode.to_json(tc)
        self.assertEqual(timecode_as_json["hours"], doubled_hours)
        self.assertEqual(timecode_as_json["minutes"], doubled_minutes)
        self.assertEqual(timecode_as_json["seconds"], doubled_seconds)
        self.assertEqual(timecode_as_json["frames"], doubled_frames)
        self.assertEqual(timecode_as_json["format"], Timecode.to_json(thirty_fps_drop_frame_format))

        timecode_from_json = Timecode.from_json(timecode_as_json)
        self.assertEqual(tc, timecode_from_json)

        expected_schema = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "hours",
                "minutes",
                "seconds",
                "frames",
                "format"
            ],
            "properties": {
                "hours": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 23
                },
                "minutes": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 59
                },
                "seconds": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 59
                },
                "frames": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 119
                },
                "format": {
                    "type": "object",
                    "description": "The timecode format is defined as a rational frame rate and - where a\nsignal with sub-frames is described, such as an interlaced signal - an\nindex of which sub-frame is referred to by the timecode.\n",
                    "required": [
                        "frameRate"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "frameRate": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "num",
                                "denom"
                            ],
                            "properties": {
                                "num": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 2147483647
                                },
                                "denom": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 4294967295
                                }
                            }
                        },
                        "subFrame": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 4294967295
                        }
                    }
                }
            },
            "description": "SMPTE timecode of the sample. Timecode is a standard for labeling\nindividual frames of data in media systems and is useful for\ninter-frame synchronization.- format.frameRate: The frame rate as a rational number. Drop frame\nrates such as 29.97 should be represented as e.g. 30000/1001. The\ntimecode frame rate may differ from the sample frequency.\n"
        }
        actual_schema = Timecode.make_json_schema()
        # TODO figure out how to normalize classic docstring massaging to match Pydantic output"
        expected_schema.pop("description", None)
        actual_schema.pop("description", None)
        self.assertEqual(expected_schema, actual_schema)

    def test_timestamp(self):
        with self.assertRaises(ValidationError):
            Timestamp('foo', 0)
        with self.assertRaises(ValidationError):
            Timestamp(0, 'bar')
        with self.assertRaises(ValidationError):
            Timestamp(0, 0.0)
        with self.assertRaises(ValidationError):
            Timestamp(0.0, 0)
        with self.assertRaises(ValidationError):
            Timestamp(-1, 0)
        with self.assertRaises(ValidationError):
            Timestamp(0, -1)
        valid_timestamp = Timestamp(3, 4)
        self.assertEqual(3, valid_timestamp.seconds)
        self.assertEqual(4, valid_timestamp.nanoseconds)
        with self.assertRaises(ValidationError):
            valid_timestamp.seconds = 'foo'
        with self.assertRaises(ValidationError):
            valid_timestamp.nanoseconds = 'bar'
        with self.assertRaises(ValidationError):
            valid_timestamp.seconds = 0.0
        with self.assertRaises(ValidationError):
            valid_timestamp.nanoseconds = 0.0
        with self.assertRaises(ValidationError):
            valid_timestamp.seconds = -1
        with self.assertRaises(ValidationError):
            valid_timestamp.nanoseconds = -1
        with self.assertRaises(ValidationError):
            Timestamp(0, -1)

        timestamp_as_json = Timestamp.to_json(valid_timestamp)
        self.assertEqual(timestamp_as_json["seconds"], 3)
        self.assertEqual(timestamp_as_json["nanoseconds"], 4)

        timestamp_from_json = Timestamp.from_json(timestamp_as_json)
        self.assertEqual(valid_timestamp, timestamp_from_json)

        expected_schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "seconds": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": MAX_UINT_48
                },
                "nanoseconds": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": MAX_UINT_32
                }
            },
            "required": ["seconds", "nanoseconds"]
        }
        actual_schema = Timestamp.make_json_schema()
        self.assertEqual(expected_schema, actual_schema)

    def test_synchronization_source_validation(self) -> None:
        # not perfect but better than nothing
        # TODO use changes in snake case to insert underscores
        self.assertListEqual([m.name.lower().replace('_','')
                              for m in SynchronizationSource],
                             [m.value.lower().replace('_','')
                              for m in SynchronizationSource])

    def test_synchronization_offsets_validation(self) -> None:
        valid_translation: float = 1.0
        valid_rotation: float = 2.0
        valid_lens_encoders: float = 3.0
        with self.assertRaises(ValidationError):
            SynchronizationOffsets(translation="foo",
                                   rotation=valid_rotation,
                                   lensEncoders=valid_lens_encoders)
        with self.assertRaises(ValidationError):
            SynchronizationOffsets(translation=valid_translation,
                                   rotation="foo",
                                   lensEncoders=valid_lens_encoders)
        with self.assertRaises(ValidationError):
            SynchronizationOffsets(translation=valid_translation,
                                   rotation=valid_rotation,
                                   lensEncoders="foo")
        valid_offsets = SynchronizationOffsets(translation=valid_translation,
                                               rotation=valid_rotation,
                                               lensEncoders=valid_lens_encoders)

        doubled_translation: float = valid_translation * 2
        doubled_rotation: float = valid_rotation * 2
        doubled_lens_encoders: float = valid_lens_encoders * 2
        valid_offsets.translation = doubled_translation
        self.assertEqual(doubled_translation, valid_offsets.translation)
        valid_offsets.rotation = doubled_rotation
        self.assertEqual(doubled_rotation, valid_offsets.rotation)
        valid_offsets.lensEncoders = doubled_lens_encoders
        self.assertEqual(doubled_lens_encoders, valid_offsets.lensEncoders)
        with self.assertRaises(ValidationError):
            valid_offsets.translation = "foo"
        with self.assertRaises(ValidationError):
            valid_offsets.rotation = "foo"
        with self.assertRaises(ValidationError):
            valid_offsets.lens_encoders = "foo"

        offsets_as_json = SynchronizationOffsets.to_json(valid_offsets)
        self.assertEqual(offsets_as_json["translation"], doubled_translation)
        self.assertEqual(offsets_as_json["rotation"], doubled_rotation)
        self.assertEqual(offsets_as_json["lensEncoders"], doubled_lens_encoders)

        offsets_from_json = SynchronizationOffsets.from_json(offsets_as_json)
        self.assertEqual(valid_offsets, offsets_from_json)

        expected_schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "translation": {
                    "anyOf": [ { "type": "number" }, { "type": "null" } ],
                    "default": None
                },
                "rotation": {
                    "anyOf": [ { "type": "number" }, {  "type": "null" } ],
                    "default": None
                },
                "lensEncoders": {
                    "anyOf": [ {  "type": "number" }, {  "type": "null" } ],
                    "default": None
                }
            }
        }
        actual_schema = SynchronizationOffsets.make_json_schema()
        # del actual_schema["description"]  # because classic camdkit doesn't include it
        self.assertDictEqual(expected_schema, actual_schema)

    def test_synchronization_ptp(self):
        min_valid_domain: int = 0
        max_valid_domain: int = MAX_INT_8
        valid_domain: int = 1
        valid_master: str = "00:11:22:33:44:55"
        valid_offset: float = 1.0
        with self.assertRaises(ValidationError):
            SynchronizationPTP(domain="foo", master=valid_master, offset=valid_offset)
        with self.assertRaises(ValidationError):
            SynchronizationPTP(domain=min_valid_domain - 1, master=valid_master, offset=valid_offset)
        with self.assertRaises(ValidationError):
            SynchronizationPTP(domain=max_valid_domain + 1, master=valid_master, offset=valid_offset)
        with self.assertRaises(ValidationError):
            SynchronizationPTP(domain=valid_domain, master=0.0, offset=valid_offset)
        with self.assertRaises(ValidationError):
            SynchronizationPTP(domain=valid_domain, master=valid_master, offset="foo")
        valid_ptp = SynchronizationPTP(domain=valid_domain, master=valid_master, offset=valid_offset)

        updated_domain: int = valid_domain * 2
        updated_master: str = "00:11:22:33:44:56"
        updated_offset: float = valid_offset * 2
        valid_ptp.domain = updated_domain
        self.assertEqual(updated_domain, valid_ptp.domain)
        valid_ptp.master = updated_master
        self.assertEqual(updated_master, valid_ptp.master)
        valid_ptp.offset = updated_offset
        self.assertEqual(updated_offset, valid_ptp.offset)
        with self.assertRaises(ValidationError):
            valid_ptp.domain = "foo"
        with self.assertRaises(ValidationError):
            valid_ptp.master = 0.0
        with self.assertRaises(ValidationError):
            valid_ptp.offset = "foo"

        ptp_as_json = SynchronizationPTP.to_json(valid_ptp)
        self.assertEqual(ptp_as_json["domain"], updated_domain)
        self.assertEqual(ptp_as_json["master"], updated_master)
        self.assertEqual(ptp_as_json["offset"], updated_offset)

        ptp_from_json = SynchronizationPTP.from_json(ptp_as_json)
        self.assertEqual(valid_ptp, ptp_from_json)

        expected_schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "master": {
                    "anyOf": [
                        {
                            "type": "string",
                            "pattern": "(?:^[0-9a-f]{2}(?::[0-9a-f]{2}){5}$)|(?:^[0-9a-f]{2}(?:-[0-9a-f]{2}){5}$)"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": None
                },
                "offset": {
                    "anyOf": [
                        {
                            "type": "number"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": None
                },
                "domain": {
                    "anyOf": [
                        {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 127
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": None
                }
            }
        }
        actual_schema = SynchronizationPTP.make_json_schema()
        # del actual_schema["description"]  # because classic camdkit doesn't include it
        self.assertDictEqual(expected_schema, actual_schema)

    def test_synchronization(self):
        valid_locked: bool = True
        valid_synchronization_source: SynchronizationSource = SynchronizationSource.GENLOCK
        valid_frequency_num = 30000
        valid_frequency_denom = 1001
        valid_frequency = StrictlyPositiveRational(valid_frequency_num, valid_frequency_denom)
        valid_translation_offset: float = 1.0
        valid_rotation_offset: float = 1.0
        valid_lens_encoders_offset: float = 1.0
        valid_offsets = SynchronizationOffsets(translation=valid_translation_offset,
                                               rotation=valid_rotation_offset,
                                               lensEncoders=valid_lens_encoders_offset)
        valid_present: bool = True
        valid_ptp_domain: int = 1
        valid_ptp_master: str = "00:11:22:33:44:55"
        valid_ptp_offset: float = 3.0
        valid_ptp = SynchronizationPTP(domain=valid_ptp_domain,
                                       master=valid_ptp_master,
                                       offset=valid_ptp_offset)
        with self.assertRaises(ValidationError):
            Synchronization(valid_locked,
                            "foo",
                            valid_frequency,
                            valid_offsets,
                            valid_present,
                            valid_ptp)
        with self.assertRaises(ValidationError):
            Synchronization(valid_locked,
                            "foo",
                            valid_frequency,
                            valid_offsets,
                            valid_present,
                            valid_ptp)
        with self.assertRaises(ValidationError):
            Synchronization(valid_locked,
                            valid_synchronization_source,
                            "foo",
                            valid_offsets,
                            valid_present,
                            valid_ptp)
        with self.assertRaises(ValidationError):
            Synchronization(valid_locked,
                            valid_synchronization_source,
                            valid_frequency,
                            "foo",
                            valid_present,
                            valid_ptp)
        with self.assertRaises(ValidationError):
            Synchronization(valid_locked,
                            valid_synchronization_source,
                            valid_frequency,
                            valid_offsets,
                            "foo",
                            valid_ptp)
        with self.assertRaises(ValidationError):
            Synchronization(valid_locked,
                            valid_synchronization_source,
                            valid_frequency,
                            valid_offsets,
                            valid_present,
                            "foo")
        valid_sync = Synchronization(valid_locked,
                                     valid_synchronization_source,
                                     valid_frequency,
                                     valid_offsets,
                                     valid_present,
                                     valid_ptp)

        updated_locked = not valid_locked
        updated_synchronization_source = SynchronizationSource.PTP
        updated_frequency = StrictlyPositiveRational(valid_frequency_num * 2, valid_frequency_denom)
        updated_translation_offset: float = valid_translation_offset * 2
        updated_rotation_offset: float = valid_rotation_offset * 2
        updated_lens_encoders_offset: float = valid_lens_encoders_offset * 2
        updated_offsets = SynchronizationOffsets(translation=updated_translation_offset,
                                                 rotation=updated_rotation_offset,
                                                 lensEncoders=updated_lens_encoders_offset)
        updated_present: bool = not valid_present
        updated_ptp_domain: int = valid_ptp_domain * 2
        updated_ptp_master: str = "00:11:22:33:44:56"
        updated_ptp_offset: float = valid_ptp_offset * 2
        updated_ptp = SynchronizationPTP(domain=updated_ptp_domain,
                                         master=updated_ptp_master,
                                         offset=updated_ptp_offset)
        valid_sync.locked = updated_locked
        self.assertEqual(updated_locked, valid_sync.locked)
        valid_sync.source = updated_synchronization_source
        valid_sync.frequency = updated_frequency
        self.assertEqual(updated_frequency, valid_sync.frequency)
        valid_sync.offsets = updated_offsets
        self.assertEqual(updated_offsets, valid_sync.offsets)
        valid_sync.present = updated_present
        self.assertEqual(updated_present, valid_sync.present)
        valid_sync.ptp = updated_ptp
        self.assertEqual(updated_ptp, valid_sync.ptp)
        with self.assertRaises(ValidationError):
            valid_sync.locked = "foo"
        with self.assertRaises(ValidationError):
            valid_sync.source = "foo"
        with self.assertRaises(ValidationError):
            valid_sync.frequency = "foo"
        with self.assertRaises(ValidationError):
            valid_sync.offsets = "foo"
        with self.assertRaises(ValidationError):
            valid_sync.present = "foo"
        with self.assertRaises(ValidationError):
            valid_sync.ptp = "foo"

        sync_as_json = Synchronization.to_json(valid_sync)
        self.assertEqual(sync_as_json["locked"], updated_locked)
        self.assertEqual(sync_as_json["source"], updated_synchronization_source)
        self.assertEqual(sync_as_json["frequency"], StrictlyPositiveRational.to_json(updated_frequency))
        self.assertEqual(sync_as_json["offsets"], SynchronizationOffsets.to_json(updated_offsets))
        self.assertEqual(sync_as_json["present"], updated_present)
        self.assertEqual(sync_as_json["ptp"], SynchronizationPTP.to_json(updated_ptp))

        sync_from_json = Synchronization.from_json(sync_as_json)
        self.assertEqual(valid_sync, sync_from_json)

        expected_schema = {
            "type": "object",
            "additionalProperties":False,
            "description": "Object describing how the tracking device is synchronized for this\nsample.\n\nfrequency: The frequency of a synchronization signal.This may differ from\nthe sample frame rate for example in a genlocked tracking device. This is\nnot required if the synchronization source is PTP or NTP.\nlocked: Is the tracking device locked to the synchronization source\noffsets: Offsets in seconds between sync and sample. Critical for e.g.\nframe remapping, or when using different data sources for\nposition/rotation and lens encoding\npresent: Is the synchronization source present (a synchronization\nsource can be present but not locked if frame rates differ for\nexample)\nptp: If the synchronization source is a PTP master, then this object\ncontains:\n- \"master\": The MAC address of the PTP master\n- \"offset\": The timing offset in seconds from the sample timestamp to\nthe PTP timestamp\n- \"domain\": The PTP domain number\nsource: The source of synchronization must be defined as one of the\nfollowing:\n- \"genlock\": The tracking device has an external black/burst or\ntri-level analog sync signal that is triggering the capture of\ntracking samples\n- \"videoIn\": The tracking device has an external video signal that is\ntriggering the capture of tracking samples\n- \"ptp\": The tracking device is locked to a PTP master\n- \"ntp\": The tracking device is locked to an NTP server\n",
            "properties": {
                "frequency": {
                    "anyOf": [
                        {
                            "type": "object",
                            "additionalProperties":False,
                            "required": [
                                "num",
                                "denom"
                            ],
                            "properties": {
                                "num": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 2147483647
                                },
                                "denom": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 4294967295
                                }
                            }
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default":None
                },
                "locked": {
                    "type": "boolean"
                },
                "offsets": {
                    "anyOf": [
                        {
                            "type": "object",
                            "additionalProperties":False,
                            "properties": {
                                "translation": {
                                    "anyOf": [
                                        {
                                            "type": "number"
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ],
                                    "default":None
                                },
                                "rotation": {
                                    "anyOf": [
                                        {
                                            "type": "number"
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ],
                                    "default":None
                                },
                                "lensEncoders": {
                                    "anyOf": [
                                        {
                                            "type": "number"
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ],
                                    "default":None
                                }
                            }
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default":None
                },
                "present": {
                    "anyOf": [
                        {
                            "type": "boolean"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default":None
                },
                "ptp": {
                    "anyOf": [
                        {
                            "type": "object",
                            "additionalProperties":False,
                            "properties": {
                                "master": {
                                    "anyOf": [
                                        {
                                            "type": "string",
                                            "pattern": "(?:^[0-9a-f]{2}(?::[0-9a-f]{2}){5}$)|(?:^[0-9a-f]{2}(?:-[0-9a-f]{2}){5}$)"
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ],
                                    "default":None
                                },
                                "offset": {
                                    "anyOf": [
                                        {
                                            "type": "number"
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ],
                                    "default":None
                                },
                                "domain": {
                                    "anyOf": [
                                        {
                                            "type": "integer",
                                            "minimum": 0,
                                            "maximum": 127
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ],
                                    "default":None
                                }
                            }
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default":None
                },
                "source": {
                    "type": "string",
                    "enum": [
                        "genlock",
                        "videoIn",
                        "ptp",
                        "ntp"
                    ]
                }
            },
            "required": [
                "locked",
                "source"
            ]
        }
        actual_schema = Synchronization.make_json_schema()
        self.assertEqual(expected_schema, actual_schema)

if __name__ == '__main__':
    unittest.main()
