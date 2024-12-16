#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for lens modeling"""

from typing import Any, Annotated, Self

from pydantic import Field, model_validator

from camdkit.compatibility import CompatibleBaseModel
from camdkit.numeric_types import (NonNegativeFloat, StrictlyPositiveFloat,
                                   NonNegativeInt, UnityOrGreaterFloat)
from camdkit.string_types import NonBlankUTF8String


class StaticLens(CompatibleBaseModel):
    distortion_overscan_max: Annotated[UnityOrGreaterFloat | None,
      Field(alias="distortionOverscanMax")] = None
    undistortion_overscan_max: Annotated[UnityOrGreaterFloat | None,
      Field(alias="undistortionOverscanMax")] = None
    make: NonBlankUTF8String | None = None
    model: NonBlankUTF8String | None = None
    serial_number: Annotated[NonBlankUTF8String | None, Field(alias="serialNumber")] = None
    firmware_version: Annotated[NonBlankUTF8String | None, Field(alias="firmwareVersion")] = None
    nominal_focal_length: Annotated[NonNegativeFloat, None, Field(alias="nominalFocalLength")] = None


class Distortion(CompatibleBaseModel):
    radial: Annotated[tuple[float, ...], Field(strict=True)]
    tangential: Annotated[tuple[float, ...] | None, Field(strict=True)] = None
    model: NonBlankUTF8String | None = None

    @model_validator(mode="after")
    def check_tuples_not_empty(self) -> Self:
        if self.radial is not None and len(self.radial) == 0:
            raise ValueError("radial distortion coefficient sequence must not be empty")
        if self.tangential is not None and len(self.tangential) == 0:
            raise ValueError("tangential distortion coefficient sequence, if provided, must not be empty")
        return self

    def __init__(self, radial: tuple[float, ...],  # positional __init__() for compatibility
                 tangential: tuple[float, ...] | None = None,
                 model: str | None = None):
        super(Distortion, self).__init__(radial=radial, tangential=tangential, model=model)


class PlanarOffset(CompatibleBaseModel):
    x: float
    y: float

    def __init__(self, x: float, y: float):
        super(PlanarOffset, self).__init__(x=x, y=y)

class DistortionOffset(PlanarOffset):

    def __init__(self, x: float, y: float):
        super(DistortionOffset, self).__init__(x=x, y=y)

class ProjectionOffset(PlanarOffset):

    def __init__(self, x: float, y: float):
        super(ProjectionOffset, self).__init__(x=x, y=y)


class FizEncoders(CompatibleBaseModel):
    focus: NonNegativeFloat | None = None
    iris: NonNegativeFloat | None = None
    zoom: NonNegativeFloat | None = None

    def __init__(self, focus: float, iris: float, zoom: float):
        super(FizEncoders, self).__init__(focus=focus, iris=iris, zoom=zoom)


class RawFizEncoders(CompatibleBaseModel):
    focus: NonNegativeInt | None = None
    iris: NonNegativeInt | None = None
    zoom: NonNegativeInt | None = None

    def __init__(self, focus: int, iris: int, zoom: int):
        super(RawFizEncoders, self).__init__(focus=focus, iris=iris, zoom=zoom)


class ExposureFalloff(CompatibleBaseModel):
    a1: float
    a2: float | None = None
    a3: float | None = None

    def __init__(self, a1: float, a2: float | None = None, a3: float | None = None):
        super(ExposureFalloff, self).__init__(a1=a1, a2=a2, a3=a3)


class Lens(CompatibleBaseModel):
    # TODO: watch GitHub issue #127 to see if we can get rid of the 'custom' field
    custom: tuple[tuple[Any, ...], ...] | None = None  # WTF?
    distortion: tuple[Distortion, ...] | None = None
    distortion_overscan: Annotated[tuple[UnityOrGreaterFloat, ...] | None, Field(alias="distortionOverscan")] = None
    undistortion_overscan: Annotated[tuple[UnityOrGreaterFloat, ...] | None, Field(alias="undistortionOverscan")] = None
    distortion_offset: Annotated[tuple[DistortionOffset, ...] | None, Field(alias="distortionOffset")] = None
    encoders: tuple[FizEncoders, ...] | None = None
    entrance_pupil_offset: Annotated[tuple[float, ...] | None, Field(alias="entrancePupilOffset")] = None
    exposure_falloff: Annotated[tuple[ExposureFalloff, ...] | None, Field(alias="exposureFalloff")] = None
    f_number: Annotated[tuple[StrictlyPositiveFloat, ...] | None, Field(alias="fStop")] = None
    # TODO: file issue to get this renamed to lens_pinhole_focal_length in the clip and pinholeFocalLength in the JSON
    focal_length: Annotated[tuple[StrictlyPositiveFloat, ...] | None, Field(alias="focalLength")] = None
    focus_distance: Annotated[tuple[StrictlyPositiveFloat, ...] | None, Field(alias="focusDistance")] = None
    projection_offset: Annotated[tuple[ProjectionOffset, ...], Field(alias="projectionOffset")] = None
    raw_encoders: Annotated[tuple[RawFizEncoders, ...] | None, Field(alias="rawEncoders")] = None
    t_number: Annotated[tuple[StrictlyPositiveFloat, ...] | None, Field(alias="tStop")] = None
    undistortion: tuple[Distortion, ...] | None = None
