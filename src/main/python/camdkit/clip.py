#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling clips"""

from typing import Optional

from pydantic import Field

from camdkit.backwards import CompatibleBaseModel
from camdkit.numeric_types import NonNegativeInt, StrictlyPositiveRational
from camdkit.lens_types import StaticLens, Lens
from camdkit.camera_types import StaticCamera
from camdkit.string_types import UUIDURN
from camdkit.tracker_types import StaticTracker, Tracker
from camdkit.timing_types import Timing
from camdkit.transform_types import Transforms


class GlobalPosition(CompatibleBaseModel):
    """Global ENU and geodetic coördinates
    Reference:. https://en.wikipedia.org/wiki/Local_tangent_plane_coordinates
    """
    E: float  # East (meters)
    N: float  # North (meters)
    U: float  # Up (meters)
    lat0: float = Field(..., ge=-90, le=90)  # latitude (degrees)
    long0: float = Field(..., ge=-180, le=180)  # longitude (degrees)
    h0: float  # height (meters)

    def __init__(self, e: float, n: float, u: float, lat0: float, long0: float, h0: float):
        super(GlobalPosition, self).__init__(E=e, N=n, U=u, lat0=lat0, long0=long0, h0=h0)


class Static(CompatibleBaseModel):
    duration: Optional[StrictlyPositiveRational] = None
    static_camera: Optional[StaticCamera] = None
    static_lens: Optional[StaticLens] = None
    static_tracker: Optional[StaticTracker] = None


class Clip(CompatibleBaseModel):
    static: Optional[Static] = None
    sample_id: Optional[tuple[UUIDURN]] = None
    source_id: Optional[tuple[UUIDURN]] = None
    source_number: Optional[tuple[NonNegativeInt]] = None
    related_sample_ids: Optional[tuple[tuple[UUIDURN]]] = None
    global_stage: Optional[tuple[GlobalPosition]] = None
    tracker: Optional[Tracker] = None
    timing: Optional[Timing] = None
    transforms: Optional[tuple[Transforms]] = None
    lens: Optional[Lens] = None

    # read and write access to static data is provided via properties

    @property
    def duration(self) -> StrictlyPositiveRational:
        return self.static.duration

    @duration.setter
    def duration(self, value) -> None:
        self.static.duration = value
