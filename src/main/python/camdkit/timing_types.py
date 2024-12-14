#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling of time-related metadata"""

from enum import Enum, verify, UNIQUE, StrEnum
from typing import Annotated

from pydantic import Field, BaseModel, field_validator

from camdkit.backwards import CompatibleBaseModel
from camdkit.numeric_types import StrictlyPositiveRational, NonNegativeInt


class TimingMode(StrEnum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class TimecodeFormat(CompatibleBaseModel):
    frame_rate: Annotated[StrictlyPositiveRational, Field(alias="frameRate")]
    sub_frame: Annotated[int, Field(alias="subFrame")] = 0

    def __init__(self, frameRate: StrictlyPositiveRational, subFrame: int):
        super(TimecodeFormat, self).__init__(frameRate=frameRate, subFrame=subFrame)


class Timecode(CompatibleBaseModel):
    hours: int = Field(..., ge=0, le=23)
    minutes: int = Field(..., ge=0, le=59)
    seconds: int = Field(..., ge=0, le=59)
    frames: int = Field(..., ge=0, le=29)
    format: TimecodeFormat

    def __init__(self, hours: int, minutes: int, seconds: int, frames: int, format: TimecodeFormat):
        super(Timecode, self).__init__(hours=hours, minutes=minutes, seconds=seconds, frames=frames,
                                       format=format)


class Timestamp(CompatibleBaseModel):
    seconds: NonNegativeInt
    nanoseconds: NonNegativeInt

    def __init__(self, seconds: NonNegativeInt, nanoseconds: NonNegativeInt):
        super(Timestamp, self).__init__(seconds=seconds, nanoseconds=nanoseconds)


@verify(UNIQUE)
class SynchronizationSource(StrEnum):
    """Synchronization sources"""

    GENLOCK = "genlock"
    VIDEO_IN = "videoIn"
    PTP = "ptp"
    NTP = "ntp"


class SynchronizationOffsets(BaseModel):
    """Synchronization offsets"""

    translation: float | None = None
    rotation: float | None = None
    lens_encoders: Annotated[float | None, Field(alias="lensEncoders")] = None

    def __init__(self, translation: float, rotation: float, lensEncoders: float) -> None:
        super(SynchronizationOffsets, self).__init__(translation=translation,
                                                     rotation=rotation,
                                                     lensEncoders=lensEncoders)


class SynchronizationPTP(BaseModel):
    """needs better explanation"""

    domain: int | None = None  # ???
    master: str | None = None  # a hostname? an IPv4 address? what?
    offset: float | None  # offset in what sense? and what units?

    def __init__(self, domain: int, master: str, offset: float) -> None:
        super(SynchronizationPTP, self).__init__(domain=domain, master=master, offset=offset)


class Synchronization(BaseModel):
    locked: bool
    source: SynchronizationSource
    frequency: StrictlyPositiveRational | None = None
    offsets: SynchronizationOffsets | None = None
    present: bool | None = None
    ptp: SynchronizationPTP

    def __init__(self, locked: bool,
                 source: SynchronizationSource,
                 frequency: StrictlyPositiveRational | None,
                 offsets: SynchronizationOffsets | None,
                 present: bool | None,
                 ptp: SynchronizationPTP) -> None:
        super(Synchronization, self).__init__(locked=locked,
                                              source=source,
                                              frequency=frequency,
                                              offsets=offsets,
                                              present=present,
                                              ptp=ptp)

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