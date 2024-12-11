#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Constrained versions of built-in numeric types"""

import sys
from typing import Final, Annotated
from pydantic import Field, StringConstraints

from camdkit.backwards import CompatibleBaseModel

__all__ = ['MIN_UINT_32', 'MAX_UINT_32',
           'MIN_INT_32', 'MAX_INT_32',
           'NonNegativeInt', 'StrictlyPositiveInt',
           'NonNegativeFloat', 'StrictlyPositiveFloat',
           'Rational', 'StrictlyPositiveRational']

MIN_UINT_32: Final[int] = 0
MAX_UINT_32: Final[int] = 2**32-1
MIN_INT_32: Final[int] = -2**31
MAX_INT_32: Final[int] = 2**31-1

type NonNegativeInt = Annotated[int, Field(..., ge=0, le=MAX_UINT_32, strict=True)]

type StrictlyPositiveInt = Annotated[int, Field(..., gt=0, le=MAX_UINT_32, strict=True)]

type NonNegativeFloat = Annotated[float, Field(..., ge=0, le=sys.float_info.max, strict=True)]

type StrictlyPositiveFloat = Annotated[float, Field(..., gt=0.0, le=sys.float_info.max, strict=True)]

# init methods because by default Pydantic BaseModel doesn't let you use positional arguments,
# and camdkit 0.9 uses that style of object instantiation


class Rational(CompatibleBaseModel):
    numerator: int = Field(..., ge=MIN_INT_32, le=MAX_INT_32, strict=True)
    denominator: int = Field(..., gt=0, le=MAX_UINT_32, strict=True)

    def __init__(self, n: int, d: int) -> None:
        super(Rational, self).__init__(numerator=n, denominator=d)


class StrictlyPositiveRational(CompatibleBaseModel):
    numerator: int = Field(..., gt=0, le=MAX_INT_32, strict=True)
    denominator: int = Field(..., gt=0, le=MAX_UINT_32, strict=True)

    def __init__(self, n: int, d: int, ) -> None:
        super(StrictlyPositiveRational, self).__init__(numerator=n, denominator=d)
