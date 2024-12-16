#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for numeric types"""

import sys
from typing import Optional
import unittest

from pydantic import ValidationError

from camdkit.backwards import CompatibleBaseModel
from camdkit.numeric_types import (MAX_INT_8, MIN_INT_32,
                                   MAX_UINT_32, MAX_UINT_48, MAX_INT_32,
                                   NonNegative8BitInt,
                                   NonNegativeInt,
                                   NonNegative48BitInt,
                                   StrictlyPositiveInt,
                                   NonNegativeFloat, StrictlyPositiveFloat,
                                   UnityOrGreaterFloat,
                                   Rational, StrictlyPositiveRational)


class NumericsTestCases(unittest.TestCase):

    def test_non_negative_8bit_int(self):
        class NonNegative8BitIntTestbed(CompatibleBaseModel):
            value: NonNegative8BitInt
        x = NonNegative8BitIntTestbed(value=0)
        with self.assertRaises(ValidationError):
            x.value = 'foo'
        with self.assertRaises(ValidationError):
            x.value = -1
        with self.assertRaises(ValidationError):
            x.value = 0.0
        x.value = 0
        self.assertEqual(0, x.value)
        x.value = 1
        self.assertEqual(1, x.value)
        x.value = MAX_INT_8
        self.assertEqual(MAX_INT_8, x.value)
        with self.assertRaises(ValidationError):
            x.value = MAX_INT_8 + 1
        expected_schema = {
            "type": "integer",
            "minimum": 0,
            "maximum": MAX_INT_8,
        }
        entire_schema = NonNegative8BitIntTestbed.make_json_schema()
        non_negative_8bit_int_schema = entire_schema["properties"]["value"]
        self.assertDictEqual(expected_schema, non_negative_8bit_int_schema)

    def test_non_negative_int(self):
        class NonNegativeIntTestbed(CompatibleBaseModel):
            value: NonNegativeInt
        x = NonNegativeIntTestbed(value=0)
        with self.assertRaises(ValidationError):
            x.value = 'foo'
        with self.assertRaises(ValidationError):
            x.value = -1
        with self.assertRaises(ValidationError):
            x.value = 0.0
        x.value = 0
        self.assertEqual(0, x.value)
        x.value = 1
        self.assertEqual(1, x.value)
        x.value = MAX_UINT_32
        self.assertEqual(MAX_UINT_32, x.value)
        with self.assertRaises(ValidationError):
            x.value = MAX_UINT_32 + 1
        expected_schema = {
            "type": "integer",
            "minimum": 0,
            "maximum": MAX_UINT_32,
        }
        entire_schema = NonNegativeIntTestbed.make_json_schema()
        non_negative_int_schema = entire_schema["properties"]["value"]
        self.assertDictEqual(expected_schema, non_negative_int_schema)

    def test_non_negative_48bit_int(self):
        class NonNegative48BitIntTestbed(CompatibleBaseModel):
            value: NonNegative48BitInt

        x = NonNegative48BitIntTestbed(value=0)
        with self.assertRaises(ValidationError):
            x.value = 'foo'
        with self.assertRaises(ValidationError):
            x.value = -1
        with self.assertRaises(ValidationError):
            x.value = 0.0
        x.value = 0
        self.assertEqual(0, x.value)
        x.value = 1
        self.assertEqual(1, x.value)
        x.value = MAX_UINT_48
        self.assertEqual(MAX_UINT_48, x.value)
        with self.assertRaises(ValidationError):
            x.value = MAX_UINT_48 + 1
        expected_schema = {
            "type": "integer",
            "minimum": 0,
            "maximum": MAX_UINT_48,
        }
        entire_schema = NonNegative48BitIntTestbed.make_json_schema()
        non_negative_int_schema = entire_schema["properties"]["value"]
        self.assertDictEqual(expected_schema, non_negative_int_schema)

    def test_strictly_positive_int(self):
        class StrictlyPositiveIntTestbed(CompatibleBaseModel):
            value: StrictlyPositiveInt
        x = StrictlyPositiveIntTestbed(value=1)
        with self.assertRaises(ValidationError):
            x.value = 'foo'
        with self.assertRaises(ValidationError):
            x.value = -1
        with self.assertRaises(ValidationError):
            x.value = 0
        with self.assertRaises(ValidationError):
            x.value = 0.0
        x.value = 1
        self.assertEqual(1, x.value)
        x.value = MAX_UINT_32
        self.assertEqual(MAX_UINT_32, x.value)
        with self.assertRaises(ValidationError):
            x.value = MAX_UINT_32 + 1
        expected_schema = {
            "type": "integer",
            "minimum": 1,
            "maximum": MAX_UINT_32
        }
        entire_schema = StrictlyPositiveIntTestbed.make_json_schema()
        strictly_positive_int_schema = entire_schema["properties"]["value"]
        self.assertDictEqual(expected_schema, strictly_positive_int_schema)

    def test_non_negative_float(self):
        class NonNegativeFloatTestbed(CompatibleBaseModel):
            value: NonNegativeFloat
        x = NonNegativeFloatTestbed(value=0)
        with self.assertRaises(ValidationError):
            x.value = 'foo'
        with self.assertRaises(ValidationError):
            x.value = -1.0
        with self.assertRaises(ValidationError):
            x.value = -sys.float_info.epsilon
        x.value = 0.0
        self.assertEqual(0.0, x.value)
        x.value = sys.float_info.epsilon
        self.assertEqual(sys.float_info.epsilon, x.value)
        x.value = 1.0
        self.assertEqual(1, x.value)
        x.value = sys.float_info.max
        self.assertEqual(sys.float_info.max, x.value)
        expected_schema = {
            "type": "number",
            "minimum": 0.0,
        }
        entire_schema = NonNegativeFloatTestbed.make_json_schema()
        non_negative_float_schema = entire_schema["properties"]["value"]
        self.assertDictEqual(expected_schema, non_negative_float_schema)

    def test_strictly_positive_float(self):
        class StrictlyPositiveFloatTestbed(CompatibleBaseModel):
            value: StrictlyPositiveFloat
        x = StrictlyPositiveFloatTestbed(value=sys.float_info.epsilon)
        with self.assertRaises(ValidationError):
            x.value = 'foo'
        with self.assertRaises(ValidationError):
            x.value = -1.0
        with self.assertRaises(ValidationError):
            x.value = -sys.float_info.epsilon
        with self.assertRaises(ValidationError):
            x.value = 0.0
        x.value = sys.float_info.epsilon
        self.assertEqual(sys.float_info.epsilon, x.value)
        x.value = 1.0
        self.assertEqual(1, x.value)
        x.value = sys.float_info.max
        self.assertEqual(sys.float_info.max, x.value)
        expected_schema = {
            "type": "number",
            "exclusiveMinimum": 0.0,
        }
        entire_schema = StrictlyPositiveFloatTestbed.make_json_schema()
        strictly_positive_float_schema = entire_schema["properties"]["value"]
        self.assertDictEqual(expected_schema, strictly_positive_float_schema)

    def test_unity_or_greater_float(self):
        class UnityOrGreaterFloatTestbed(CompatibleBaseModel):
            value: UnityOrGreaterFloat
        x = UnityOrGreaterFloatTestbed(value=1.0)
        with self.assertRaises(ValidationError):
            x.value = 'foo'
        with self.assertRaises(ValidationError):
            x.value = -1.0
        with self.assertRaises(ValidationError):
            x.value = -sys.float_info.epsilon
        with self.assertRaises(ValidationError):
            x.value = 0.0
        with self.assertRaises(ValidationError):
            x.value = sys.float_info.epsilon
        with self.assertRaises(ValidationError):
            x.value = 1.0 - sys.float_info.epsilon
        x.value = 1.0
        self.assertEqual(1, x.value)
        expected_schema = {
            "type": "number",
            "minimum": 1.0,
        }
        entire_schema = UnityOrGreaterFloatTestbed.make_json_schema()
        unity_or_greater_float_schema = entire_schema["properties"]["value"]
        self.assertDictEqual(expected_schema, unity_or_greater_float_schema)

    def test_rational(self):
        with self.assertRaises(ValidationError):
            Rational(MIN_INT_32 - 1, 1)
        Rational(MIN_INT_32, 1)
        Rational(0, 1)
        Rational(MAX_INT_32, 1)
        with self.assertRaises(ValidationError):
            Rational(MAX_INT_32 + 1, 1)
        with self.assertRaises(ValidationError):
            Rational(0, MAX_UINT_32+1)
        with self.assertRaises(ValidationError):
            Rational(0, -1)
        with self.assertRaises(ValidationError):
            Rational(0, 0)
        Rational(1, 1)
        Rational(0, MAX_UINT_32)
        with self.assertRaises(ValidationError):
            Rational(0, MAX_UINT_32 +1)
        expected_schema = {
            "type": "object",
            "properties": {
                "num" : {
                    "type": "integer",
                    "minimum": MIN_INT_32,
                    "maximum": MAX_INT_32
                },
                "denom" : {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": MAX_UINT_32
                }
            },
            "required": ["num", "denom" ],
            "additionalProperties": False
        }
        schema = Rational.make_json_schema()
        self.assertDictEqual(expected_schema, schema)

    def test_strictly_positive_rational(self):
        with self.assertRaises(ValidationError):
            StrictlyPositiveRational(MIN_INT_32 - 1, 1)
        with self.assertRaises(ValidationError):
            StrictlyPositiveRational(MIN_INT_32, 1)
        with self.assertRaises(ValidationError):
            StrictlyPositiveRational(0, 1)
            StrictlyPositiveRational(1, 1)
        StrictlyPositiveRational(MAX_INT_32, 1)
        with self.assertRaises(ValidationError):
            StrictlyPositiveRational(MAX_INT_32 + 1, 1)
        with self.assertRaises(ValidationError):
            StrictlyPositiveRational(0, 1)
        with self.assertRaises(ValidationError):
            StrictlyPositiveRational(1, MAX_UINT_32+1)
        with self.assertRaises(ValidationError):
            StrictlyPositiveRational(1, -1)
        with self.assertRaises(ValidationError):
            StrictlyPositiveRational(1, 0)
        StrictlyPositiveRational(1, 1)
        StrictlyPositiveRational(1, MAX_UINT_32)
        with self.assertRaises(ValidationError):
            StrictlyPositiveRational(1, MAX_UINT_32 +1)
        # TODO file Issue: existing implementation has StrictlyPositiveRational that allows 0/N
        expected_schema = {
            "type": "object",
            "properties": {
                "num" : {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": MAX_INT_32
                },
                "denom" : {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": MAX_UINT_32
                }
            },
            "required": ["num", "denom" ],
            "additionalProperties": False
        }
        schema = StrictlyPositiveRational.make_json_schema()
        self.assertDictEqual(expected_schema, schema)


if __name__ == '__main__':
    unittest.main()
