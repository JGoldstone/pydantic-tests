#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling of tracker-related metadata"""

from typing import Annotated, Optional

from pydantic import Field

from camdkit.string_types import NonBlankUTF8String
from camdkit.backwards import CompatibleBaseModel


class StaticTracker(CompatibleBaseModel):
    make: Optional[NonBlankUTF8String] = None
    model_name: Optional[NonBlankUTF8String] = None
    serial_number: Optional[NonBlankUTF8String] = None
    firmware_version: Optional[NonBlankUTF8String] = None


class Tracker(CompatibleBaseModel):
    notes: Optional[tuple[NonBlankUTF8String, ...]] = None
    recording: Optional[tuple[Annotated[bool, Field(strict=True)], ...]] = None
    slate: Optional[tuple[NonBlankUTF8String, ...]] = None
    status: Optional[tuple[NonBlankUTF8String, ...]] = None
