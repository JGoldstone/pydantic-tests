from enum import Enum
from typing import Optional

from pydantic import Field

from camdkit.backwards import CompatibleBaseModel
from camdkit.base_types import StrictlyPositiveRational, NonNegativeInt
from camdkit.model_types import Synchronization


class TimingMode(Enum):
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


class Timing(CompatibleBaseModel):
    mode: Optional[tuple[TimingMode]] = None
    recorded_timestamp: Optional[tuple[Timestamp]] = None
    sample_rate: Optional[tuple[StrictlyPositiveRational]] = None
    sample_timestamp: Optional[tuple[Timestamp]] = None
    sequence_number: Optional[tuple[NonNegativeInt]] = None
    synchronization: Optional[tuple[Synchronization]] = None
    timecode: Optional[tuple[Timecode]] = None
