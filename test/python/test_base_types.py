import unittest
from camdkit.base_types import (MIN_UINT_32, MIN_INT_32, MAX_UINT_32, MAX_INT_32,
                                Rational, StrictlyPositiveRational, NonBlankUTF8String)
from pydantic import ValidationError


class FrameworkTestCases(unittest.TestCase):

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

    def test_non_blank_utf8_string(self):
        with self.assertRaises(ValidationError):
            NonBlankUTF8String('')
        with self.assertRaises(ValidationError):
            NonBlankUTF8String(0)
        with self.assertRaises(ValidationError):
            NonBlankUTF8String(complex(1, 1))
        NonBlankUTF8String('hello world')
        NonBlankUTF8String('X' * 1023)
        with self.assertRaises(ValidationError):
            NonBlankUTF8String('X' * 1024)


if __name__ == '__main__':
    unittest.main()
