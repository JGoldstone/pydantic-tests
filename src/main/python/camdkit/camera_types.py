#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for camera modeling"""

import math
import numbers
from fractions import Fraction

from typing import Annotated, Optional

from pydantic import Field, field_validator, StringConstraints

from camdkit.compatibility import CompatibleBaseModel
from camdkit.numeric_types import (MAX_INT_32,
                                   StrictlyPositiveInt,
                                   StrictlyPositiveRational, rationalize_strictly_and_positively)
from camdkit.string_types import NonBlankUTF8String, UUIDURN, UUID_URN_PATTERN


# Tempting as it might seem to make PhysicalDimensions and SenselDimensions subclasses
# of a single generic Dimension[T] class, that doesn't work play well with the Field
# annotations, unfortunately. Maybe someone smart will figure out how to make this idea
# work, but for now it's a wish, not something for a to-do list.


class PhysicalDimensions(CompatibleBaseModel):
    height: Annotated[float, Field(ge=0.0, lt=math.inf)]
    width: Annotated[float, Field(ge=0.0, lt=math.inf)]

    def __init__(self, width: float, height: float) -> None:
        super(PhysicalDimensions, self).__init__(width=width, height=height)


class SenselDimensions(CompatibleBaseModel):
    height: Annotated[int, Field(ge=0, le=MAX_INT_32)]
    width: Annotated[int, Field(ge=0, le=MAX_INT_32)]

    def __init__(self, width: int, height: int) -> None:
        super(SenselDimensions, self).__init__(width=width, height=height)


type ShutterAngle = Annotated[float, Field(ge=0.0, le=360.0, strict=True)]


class StaticCamera(CompatibleBaseModel):
    capture_frame_rate: Annotated[StrictlyPositiveRational | None, Field(alias="captureFrameRate")] = None
    active_sensor_physical_dimensions: Annotated[PhysicalDimensions | None, Field(alias="activeSensorPhysicalDimensions")] = None
    active_sensor_resolution: Annotated[SenselDimensions | None, Field(alias="activeSensorResolution")] = None
    make: NonBlankUTF8String | None = None
    model: NonBlankUTF8String | None = None
    serial_number: Annotated[NonBlankUTF8String | None, Field(alias="serialNumber")] = None
    firmware_version: Annotated[NonBlankUTF8String | None, Field(alias="firmwareVersion")] = None
    label: NonBlankUTF8String | None = None
    anamorphic_squeeze: Annotated[StrictlyPositiveRational | None, Field(alias="anamorphicSqueeze")] = None
    iso: Annotated[int | None, Field(gt=0, strict=True, alias="isoSpeed")] = None
    fdl_link: Annotated[str | None, Field(pattern=UUID_URN_PATTERN, alias="fdlLink")] = None
    shutter_angle: Annotated[float | None, Field(ge=0.0, le=360.0, alias="shutterAngle")] = None

    # noinspection PyNestedDecorators
    @field_validator("capture_frame_rate", "anamorphic_squeeze", mode="before")
    @classmethod
    def coerce_camera_type_to_strictly_positive_rational(cls, v):
        return rationalize_strictly_and_positively(v)


if __name__ == '__main__':
    sc = StaticCamera()
    sc.capture_frame_rate = StrictlyPositiveRational(24000, 1001)
    print('StrictlyPositiveRational accepted')
    sc.capture_frame_rate = Fraction(24000, 1001)
    sc.anamorphic_squeeze = Fraction(4, 3)
    print('Fraction accepted')
