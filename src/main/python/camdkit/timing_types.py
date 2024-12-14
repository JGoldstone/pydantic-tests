#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling of time-related metadata"""

from enum import Enum, verify, UNIQUE, StrEnum
from typing import Annotated, Optional

from pydantic import Field, BaseModel, field_validator

from camdkit.backwards import CompatibleBaseModel
from camdkit.numeric_types import StrictlyPositiveRational, NonNegativeInt


class TimingMode(StrEnum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class TimecodeFormat(CompatibleBaseModel):
    frame_rate: StrictlyPositiveRational
    sub_frame: int = 0

    def __init__(self, f_r: StrictlyPositiveRational, s_f: int):
        super(TimecodeFormat, self).__init__(frame_rate=f_r, sub_frame=s_f)


class Timecode(CompatibleBaseModel):
    hours: int = Field(..., ge=0, le=23)
    minutes: int = Field(..., ge=0, le=59)
    seconds: int = Field(..., ge=0, le=59)
    frames: int = Field(..., ge=0, le=29)
    format: TimecodeFormat

    def __init__(self, h: int, m: int, s: int, fr: int, fo: TimecodeFormat):
        super(Timecode, self).__init__(hours=h, minutes=m, seconds=s, frames=fr,
                                       format=fo)


class Timestamp(CompatibleBaseModel):
    seconds: NonNegativeInt
    nanoseconds: NonNegativeInt

    def __init__(self, s: NonNegativeInt, n: NonNegativeInt):
        super(Timestamp, self).__init__(seconds=s, nanoseconds=n)


@verify(UNIQUE)
class SynchronizationSource(StrEnum):
    """Synchronization sources"""

    GENLOCK = "genlock"
    VIDEO_IN = "videoIn"
    PTP = "ptp"
    NTP = "ntp"


class SynchronizationOffsets(BaseModel):
    """Synchronization offsets"""

    translation: Optional[float] = None
    rotation: Optional[float] = None
    lens_encoders: Optional[float] = None

    def __init__(self, translation: float, rotation: float, lens_encoders: float) -> None:
        super(SynchronizationOffsets, self).__init__(translation=translation,
                                                     rotation=rotation,
                                                     lens_encoders=lens_encoders)


class SynchronizationPTP(BaseModel):
    """needs better explanation"""

    domain: Optional[int] = None  # ???
    master: Optional[str] = None  # a hostname? an IPv4 address? what?
    offset: Optional[float]  # offset in what sense? and what units?

    def __init__(self, d: int, m: str, o: float) -> None:
        super(SynchronizationPTP, self).__init__(domain=d, master=m, offset=o)


class Synchronization(BaseModel):
    locked: bool
    source: SynchronizationSource
    frequency: Optional[StrictlyPositiveRational] = None
    offsets: Optional[SynchronizationOffsets] = None
    present: Optional[bool] = None
    ptp: SynchronizationPTP



class Timing(CompatibleBaseModel):
    mode: tuple[TimingMode, ...] | None = None
    recorded_timestamp: Annotated[tuple[Timestamp, ...], Field(alias="recordedTimestamp")] = None
    sample_rate: Annotated[tuple[StrictlyPositiveRational, ...] | None, Field(alias="sampleRate")] = None
    sample_timestamp: Annotated[tuple[Timestamp, ...] | None, Field(alias="sampleTimestamp")] = None
    sequence_number: Annotated[tuple[NonNegativeInt, ...] | None, Field(alias="sequenceNumber")] = None
    synchronization: tuple[Synchronization, ...] | None = None
    timecode: tuple[Timecode, ...] | None = None

    # @field_validator("mode", mode="before")
    # @classmethod
    # def enumify(cls, v):
    #     if isinstance(v, tuple):
    #         try:
    #             result = [TimingMode(elem) for elem in v]
    #             return result
    #             # return TimingMode(v)
    #         except ValueError:
    #             pass
    #     return v


class Sampling(Enum):
    STATIC = 'static'
    REGULAR = 'regular'


class FrameRate(StrictlyPositiveRational):
    canonical_name: str = 'captureRate'
    sampling: Sampling = Sampling.REGULAR
    units: str = "hertz"
    section: str = "camera"