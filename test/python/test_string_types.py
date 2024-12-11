#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Tests for string types"""

import unittest
import uuid

from typing import Optional

from pydantic import ValidationError

from camdkit.backwards import CompatibleBaseModel
from camdkit.string_types import NonBlankUTF8String, UUIDURN

VALID_SAMPLE_ID_URN_0 = "urn:uuid:5ca5f233-11b5-4f43-8815-948d73e48a33"
VALID_SAMPLE_ID_URN_1 = "urn:uuid:5ca5f233-11b5-dead-beef-948d73e48a33"


class StringsTestCases(unittest.TestCase):

    def test_non_blank_utf8_string(self):
        class NonBlankUTF8StringTestbed(CompatibleBaseModel):
            value: Optional[NonBlankUTF8String] = None

        x = NonBlankUTF8StringTestbed()
        self.assertIsNone(x.value)
        with self.assertRaises(ValidationError):
            x.value = 1
        with self.assertRaises(ValidationError):
            x.value = ""
        smallest_valid_non_blank_utf8_string: NonBlankUTF8String = "x"
        x.value = smallest_valid_non_blank_utf8_string
        self.assertEqual(smallest_valid_non_blank_utf8_string, x.value)
        largest_valid_non_blank_utf8_string: NonBlankUTF8String = "x" * 1023
        x.value = largest_valid_non_blank_utf8_string
        self.assertEqual(largest_valid_non_blank_utf8_string, x.value)
        smallest_too_long_non_blank_utf8_string: NonBlankUTF8String = "x" * 1024
        with self.assertRaises(ValidationError):
            x.value = smallest_too_long_non_blank_utf8_string

    def test_uuid_urn(self):
        class UUIDTestbed(CompatibleBaseModel):
            value: Optional[UUIDURN] = None

        x = UUIDTestbed()
        self.assertIsNone(x.value)
        with self.assertRaises(ValidationError):
            x.value = 1
        with self.assertRaises(ValidationError):
            x.value = ""
        with self.assertRaises(ValidationError):
            x.value = "fail"
        x.value = VALID_SAMPLE_ID_URN_0
        self.assertEqual(VALID_SAMPLE_ID_URN_0, x.value)
        x.value = VALID_SAMPLE_ID_URN_1
        self.assertEqual(VALID_SAMPLE_ID_URN_1, x.value)


if __name__ == '__main__':
    unittest.main()
