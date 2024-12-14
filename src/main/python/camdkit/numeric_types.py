#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Constrained versions of built-in numeric types"""

import sys
import numbers
from fractions import Fraction
from typing import Any, Final, Annotated
from annotated_types import Predicate
from pydantic import Field, StringConstraints

from camdkit.backwards import CompatibleBaseModel

__all__ = ['MIN_UINT_32', 'MAX_UINT_32',
           'MIN_INT_32', 'MAX_INT_32',
           'NonNegativeInt', 'StrictlyPositiveInt',
           'NonNegativeFloat', 'StrictlyPositiveFloat', 'UnityOrGreaterFloat',
           'Rational', 'StrictlyPositiveRational', 'rationalize_strictly_and_positively']

MIN_UINT_32: Final[int] = 0
MAX_UINT_32: Final[int] = 2**32-1
MIN_INT_32: Final[int] = -2**31
MAX_INT_32: Final[int] = 2**31-1

type NonNegativeInt = Annotated[int, Field(..., ge=0, le=MAX_UINT_32, strict=True)]

type StrictlyPositiveInt = Annotated[int, Field(..., gt=0, le=MAX_UINT_32, strict=True)]

type NonNegativeFloat = Annotated[float, Field(..., ge=0, le=sys.float_info.max, strict=True)]

type StrictlyPositiveFloat = Annotated[float, Field(..., gt=0.0, le=sys.float_info.max, strict=True)]

type UnityOrGreaterFloat = Annotated[float, Field(..., ge=1, le=sys.float_info.max, strict=True)]

# init methods because by default Pydantic BaseModel doesn't let you use positional arguments,
# and camdkit 0.9 uses that style of object instantiation

class Rational(CompatibleBaseModel):
    num: int = Field(ge=MIN_INT_32, le=MAX_INT_32, strict=True)
    denom: int = Field(ge=1, le=MAX_UINT_32, strict=True)

    def __init__(self, num: int, denom: int) -> None:
        super(Rational, self).__init__(num=num, denom=denom)


class StrictlyPositiveRational(CompatibleBaseModel):
    num: int = Field(ge=1, le=MAX_INT_32, strict=True)
    denom: int = Field(ge=1, le=MAX_UINT_32, strict=True)

    def __init__(self, num: int, denom: int, ) -> None:
        super(StrictlyPositiveRational, self).__init__(num=num, denom=denom)

def rationalize_strictly_and_positively(x: Any) -> StrictlyPositiveRational:
    if not isinstance(x, StrictlyPositiveRational):
        if isinstance(x, numbers.Rational):
            return StrictlyPositiveRational(int(x.numerator), int(x.denominator))
        elif isinstance(x, dict) and len(x) == 2 and "num" in x and "denom" in x:
            return StrictlyPositiveRational(int(x["num"]), int(x["denom"]))
        raise ValueError(f"could not convert input of type {type(x)} to a StrictlyPositiveRational")
    return x

# looked promising at first, and might work in clever IDE, but Pydantic can't serialize the type
# constraint when generating JSON schema -- not to mention that JSON's support for Fraction is
# half-baked: json.dumps() turns a Fraction into a string "n/d", but json.loads() has no provision
# for turning that "n/d" into "Fraction(n, d)")
#
# StrictlyPositiveRational = Annotated[Fraction, Predicate(lambda f:  0 < f.numerator <= MAX_INT_32
#                                                                 and 0 < f.denominator <= MAX_UINT_32)]




