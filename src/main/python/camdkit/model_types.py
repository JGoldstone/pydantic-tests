#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for general modeling"""

from typing import Optional, Annotated
from enum import Enum, StrEnum, verify, UNIQUE
import math

from pydantic import Field, BaseModel

from camdkit.numeric_types import StrictlyPositiveRational
from camdkit.backwards import CompatibleBaseModel, PODModel


class Sampling(Enum):
    STATIC = 'static'
    REGULAR = 'regular'


class FrameRate(StrictlyPositiveRational):
    canonical_name: str = 'captureRate'
    sampling: Sampling = Sampling.REGULAR
    units: str = "hertz"
    section: str = "camera"


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
