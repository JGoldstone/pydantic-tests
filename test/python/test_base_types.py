import sys
import unittest

from pydantic import ValidationError

from camdkit.base_types import (MIN_INT_32, MAX_UINT_32, MAX_INT_32,
                                NonNegativeInt, StrictlyPositiveInt,
                                NonNegativeFloat, StrictlyPositiveFloat,
                                Rational, StrictlyPositiveRational,
                                NonBlankUTF8String)


class FrameworkTestCases(unittest.TestCase):

    # def test_non_negative_int(self):
    #     with self.assertRaises(ValidationError):
    #         NonNegativeInt('foo')
    #     with self.assertRaises(ValidationError):
    #         NonNegativeInt(1.0)
    #     with self.assertRaises(ValidationError):
    #         NonNegativeInt(-1)
    #     NonNegativeInt(0)
    #     NonNegativeInt(1)
    #     NonNegativeInt(MAX_UINT_32)
    #     with self.assertRaises(ValidationError):
    #         NonNegativeInt(MAX_UINT_32 + 1)
    #     # TODO test validate(), to_json(), from_json() and make_json_schema()

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

    # def test_non_negative_float(self):
    #     with self.assertRaises(ValidationError):
    #         NonNegativeFloat(0+1j)
    #     with self.assertRaises(ValidationError):
    #         NonNegativeFloat(-0.1)
    #     NonNegativeFloat(0.0)
    #     NonNegativeFloat(0.1)
    #     NonNegativeFloat(sys.float_info.max)

    # def test_strictly_positive_float(self):
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveFloat(1+1j)
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveFloat(-0.1)
    #     with self.assertRaises(ValidationError):
    #         StrictlyPositiveFloat(0.0)
    #     StrictlyPositiveFloat(0.1)
    #     StrictlyPositiveFloat(sys.float_info.max)

    def test_rational_ranges(self):
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

    def test_strictly_positive_rational_ranges(self):
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

    # def test_non_blank_utf8_string(self):
    #     # with self.assertRaises(ValidationError):
    #     #     a: NonBlankUTF8String = ''
    #     with self.assertRaises(ValidationError):
    #         b: NonBlankUTF8String = 0
    #     with self.assertRaises(ValidationError):
    #         c: NonBlankUTF8String = complex(1, 1)
    #     d: NonBlankUTF8String = 'hello world'
    #     e: NonBlankUTF8String = 'X' * 1023
    #     with self.assertRaises(ValidationError):
    #         f: NonBlankUTF8String = 'X' * 1024

if __name__ == '__main__':
    unittest.main()
