#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling of spatial transforms"""

from typing import Optional

from pydantic import Field

from camdkit.backwards import CompatibleBaseModel
from camdkit.string_types import UUIDURN


class Vector3(CompatibleBaseModel):
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        super(Vector3, self).__init__(x=x, y=y, z=z)


class Rotator3(CompatibleBaseModel):
    x: float  # pan
    y: float  # tilt
    z: float  # roll

    def __init__(self, x: float, y: float, z: float):
        super(Rotator3, self).__init__(x=x, y=y, z=z)


class Transforms(CompatibleBaseModel):
    translation: Vector3
    rotation: Rotator3
    scale: Optional[Vector3] = None
    id: Optional[UUIDURN] = None
    parent_id: Optional[UUIDURN] = None
