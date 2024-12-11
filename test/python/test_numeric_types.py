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
from camdkit.numeric_types import (MIN_INT_32, MAX_UINT_32, MAX_INT_32,
                                   NonNegativeInt, StrictlyPositiveInt,
                                   NonNegativeFloat, StrictlyPositiveFloat,
                                   Rational, StrictlyPositiveRational)


class NumericsTestCases(unittest.TestCase):

    def test_non_negative_int(self):
        class NonNegativeIntTestbed(CompatibleBaseModel):
            x: Optional[NonNegativeInt] = None


        with self.assertRaises(ValidationError):
            class WrongType(CompatibleBaseModel):
                value: NonNegativeInt

            x = NonNegativeIntTestbed()
            with self.assertRaises(ValidationError):
                x.value = 'foo'
            with self.assertRaises(ValidationError):
                x.value = -1
            with self.assertRaises(ValidationError):
                x.value = 0 - sys.float_info.epsilon
            with self.assertRaises(ValidationError):
                x.value = 0.0
            x.value = 0
            self.assertEqual(0, x.value)
            x.value = 1
            self.assertEqual(1, x.value)
            x.value = MAX_UINT_32
            self.assertEqual(MAX_UINT_32, x.value)
            with self.assertRaises(ValidationError):
                x = MAX_UINT_32 + 1

    # TODO: write test cases for StrictlyPositiveInt
    # def test_strictly_positive_int(self):
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveInt('bar')
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveInt(1.0)
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveInt(-1)
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveInt(0)
    #     StrictlyPositiveInt(1)
    #     StrictlyPositiveInt(MAX_UINT_32)
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveInt(MAX_UINT_32 + 1)

    # TODO: write test cases for NonNegativeFloat
    # def test_non_negative_float(self):
    #     with self.assertRaises(ValidationError):
    #         NonNegativeFloat(0+1j)
    #     with self.assertRaises(ValidationError):
    #         NonNegativeFloat(-0.1)
    #     NonNegativeFloat(0.0)
    #     NonNegativeFloat(0.1)
    #     NonNegativeFloat(sys.float_info.max)

    # TODO: write test cases for StrictlyPositiveFloat
    # def test_strictly_positive_float(self):
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveFloat(1+1j)
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveFloat(-0.1)
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveFloat(0.0)
    #     StrictlyPositiveFloat(0.1)
    #     StrictlyPositiveFloat(sys.float_info.max)

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


if __name__ == '__main__':
    unittest.main()
