#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for lens modeling"""

from typing import Optional, Annotated, Self

from pydantic import Field, model_validator

from camdkit.backwards import CompatibleBaseModel
from camdkit.numeric_types import (NonNegativeFloat, StrictlyPositiveFloat,
                                   NonNegativeInt)
from camdkit.string_types import NonBlankUTF8String


class StaticLens(CompatibleBaseModel):
    distortion_overscan_max: Optional[StrictlyPositiveFloat] = None
    undistortion_overscan_max: Optional[StrictlyPositiveFloat] = None
    make: Optional[NonBlankUTF8String] = None
    model_name: Optional[NonBlankUTF8String] = None
    serial_number: Optional[NonBlankUTF8String] = None
    firmware_version: Optional[NonBlankUTF8String] = None
    nominal_focal_length: Optional[StrictlyPositiveFloat] = None


class Distortion(CompatibleBaseModel):
    radial: tuple[Annotated[float, Field(strict=True)], ...]
    tangential: Optional[tuple[Annotated[float, Field(strict=True)], ...]] = None
    model: Optional[NonBlankUTF8String] = None

    @model_validator(mode="after")
    def check_tuples_not_empty(self) -> Self:
        if self.radial is not None and len(self.radial) == 0:
            raise ValueError("radial distortion coefficient sequence must not be empty")
        if self.tangential is not None and len(self.tangential) == 0:
            raise ValueError("tangential distortion coefficient sequence, if provided, must not be empty")
        return self

    def __init__(self, radial: tuple[float, ...],  # positional __init__() for compatibility
                 tangential: Optional[tuple[float, ...]] = None,
                 model: Optional[str] = None):
        super(Distortion, self).__init__(radial=radial, tangential=tangential, model=model)


class PlanarOffset(CompatibleBaseModel):
    x: float
    y: float

    def __init__(self, x: float, y: float):
        super(PlanarOffset, self).__init__(x=x, y=y)


class FizEncoder[T](CompatibleBaseModel):
    focus: T
    iris: T
    zoom: T


class ExposureFalloff(CompatibleBaseModel):
    a1: float
    a2: Optional[float] = None
    a3: Optional[float] = None


class Lens(CompatibleBaseModel):
    custom: Optional[tuple[tuple]] = None  # WTF?
    distortion: Optional[tuple[Distortion]] = None
    distortion_overscan: Optional[tuple[tuple[float]]] = None  # How many, exactly?
    undistortion_overscan: Optional[tuple[tuple[float]]] = None  # Again, how many?
    distortion_offset: Optional[tuple[tuple[PlanarOffset]]] = None
    encoders: Optional[tuple[tuple[FizEncoder[NonNegativeFloat]]]] = None
    entrance_pupil_offset: Optional[tuple[float]] = None
    exposure_falloff: Optional[tuple[ExposureFalloff]] = None
    f_number: Optional[tuple[StrictlyPositiveFloat]] = None
    focal_length: Optional[tuple[StrictlyPositiveFloat]] = None
    focus_distance: Optional[tuple[StrictlyPositiveFloat]] = None
    projection_offset: Optional[tuple[PlanarOffset]] = None
    raw_encoders: Optional[tuple[FizEncoder[NonNegativeInt]]] = None
    t_number: Optional[tuple[StrictlyPositiveFloat]] = None
    undistortion: Optional[tuple[Distortion]] = None
