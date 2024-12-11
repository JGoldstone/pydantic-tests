#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Tests for string types"""

import unittest

from typing import Optional

from pydantic import ValidationError

from camdkit.backwards import CompatibleBaseModel
from camdkit.string_types import NonBlankUTF8String


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


if __name__ == '__main__':
    unittest.main()
