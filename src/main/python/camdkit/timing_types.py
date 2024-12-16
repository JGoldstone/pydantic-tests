#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling of time-related metadata"""

from enum import Enum, verify, UNIQUE, StrEnum
from typing import Annotated, Optional

from pydantic import Field

from camdkit.backwards import CompatibleBaseModel
from camdkit.numeric_types import (StrictlyPositiveRational,
                                   NonNegative8BitInt,
                                   NonNegativeInt,
                                   NonNegative48BitInt)

PTP_MASTER_PATTERN = "^([A-F0-9]{2}:){5}[A-F0-9]{2}$"

class TimingMode(StrEnum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class TimecodeFormat(CompatibleBaseModel):
    """The timecode format is defined as a rational frame rate and - where a
    signal with sub-frames is described, such as an interlaced signal - an
    index of which sub-frame is referred to by the timecode.
    """
    frame_rate: Annotated[StrictlyPositiveRational, Field(alias="frameRate")]
    sub_frame: Annotated[NonNegativeInt, Field(alias="subFrame", strict=True)] = 0

    def __init__(self, frameRate: StrictlyPositiveRational, subFrame: int):
        super(TimecodeFormat, self).__init__(frameRate=frameRate, subFrame=subFrame)


class Timecode(CompatibleBaseModel):
    """SMPTE timecode of the sample. Timecode is a standard for labeling
    individual frames of data in media systems and is useful for
    inter-frame synchronization.- format.frameRate: The frame rate as a rational number. Drop frame
    rates such as 29.97 should be represented as e.g. 30000/1001. The
    timecode frame rate may differ from the sample frequency.
    """
    hours: int = Field(..., ge=0, le=23, strict=True)
    minutes: int = Field(..., ge=0, le=59, strict=True)
    seconds: int = Field(..., ge=0, le=59, strict=True)
    frames: int = Field(..., ge=0, le=119, strict=True)
    format: TimecodeFormat

    def __init__(self, hours: int, minutes: int, seconds: int, frames: int, format: TimecodeFormat):
        super(Timecode, self).__init__(hours=hours, minutes=minutes, seconds=seconds, frames=frames,
                                       format=format)


class Timestamp(CompatibleBaseModel):
    seconds: NonNegative48BitInt
    nanoseconds: NonNegativeInt

    def __init__(self, seconds: NonNegativeInt, nanoseconds: NonNegativeInt):
        super(Timestamp, self).__init__(seconds=seconds, nanoseconds=nanoseconds)


@verify(UNIQUE)
class SynchronizationSource(StrEnum):

    GENLOCK = "genlock"
    VIDEO_IN = "videoIn"
    PTP = "ptp"
    NTP = "ntp"


class SynchronizationOffsets(CompatibleBaseModel):

    translation: float | None = None
    rotation: float | None = None
    lens_encoders: Annotated[float | None, Field(alias="lensEncoders")] = None

    # def __init__(self, translation: float, rotation: float, lensEncoders: float) -> None:
    #     super(SynchronizationOffsets, self).__init__(translation=translation,
    #                                                  rotation=rotation,
    #                                                  lensEncoders=lensEncoders)


class SynchronizationPTP(CompatibleBaseModel):

    domain: NonNegative8BitInt | None = None
    master: Annotated[str | None, Field(pattern=PTP_MASTER_PATTERN)] = None
    offset: float | None = None

    # def __init__(self, domain: Optional[int],
    #              master: Optional[str],
    #              offset: Optional[float]) -> None:
    #     super(SynchronizationPTP, self).__init__(domain=domain, master=master, offset=offset)


class Synchronization(CompatibleBaseModel):
    """Object describing how the tracking device is synchronized for this
    sample.

    frequency: The frequency of a synchronization signal.This may differ from
    the sample frame rate for example in a genlocked tracking device. This is
    not required if the synchronization source is PTP or NTP.
    locked: Is the tracking device locked to the synchronization source
    offsets: Offsets in seconds between sync and sample. Critical for e.g.
    frame remapping, or when using different data sources for
    position/rotation and lens encoding
    present: Is the synchronization source present (a synchronization
    source can be present but not locked if frame rates differ for
    example)
    ptp: If the synchronization source is a PTP master, then this object
    contains:
    - "master": The MAC address of the PTP master
    - "offset": The timing offset in seconds from the sample timestamp to
    the PTP timestamp
    - "domain": The PTP domain number
    source: The source of synchronization must be defined as one of the
    following:
    - "genlock": The tracking device has an external black/burst or
    tri-level analog sync signal that is triggering the capture of
    tracking samples
    - "videoIn": The tracking device has an external video signal that is
    triggering the capture of tracking samples
    - "ptp": The tracking device is locked to a PTP master
    - "ntp": The tracking device is locked to an NTP server
    """
    locked: bool
    source: SynchronizationSource
    frequency: StrictlyPositiveRational | None = None
    offsets: SynchronizationOffsets | None = None
    present: bool | None = None
    ptp: SynchronizationPTP | None = None

    def __init__(self, locked: bool,
                 source: SynchronizationSource,
                 frequency: StrictlyPositiveRational | None,
                 offsets: SynchronizationOffsets | None,
                 present: bool | None,
                 ptp: SynchronizationPTP | None) -> None:
        super(Synchronization, self).__init__(locked=locked,
                                              source=source,
                                              frequency=frequency,
                                              offsets=offsets,
                                              present=present,
                                              ptp=ptp)


class Timing(CompatibleBaseModel):
    mode: tuple[TimingMode, ...] | None = None
    recorded_timestamp: Annotated[tuple[Timestamp, ...] | None, Field(alias="recordedTimestamp")] = None
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
