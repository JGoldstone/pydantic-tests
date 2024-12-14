#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling of tracker-related metadata"""

from typing import Annotated

from pydantic import Field

from camdkit.string_types import NonBlankUTF8String
from camdkit.backwards import CompatibleBaseModel


class StaticTracker(CompatibleBaseModel):
    make: NonBlankUTF8String | None = None
    model: NonBlankUTF8String | None = None
    serial_number: Annotated[NonBlankUTF8String | None, Field(alias="serialNumber")] = None
    firmware: Annotated[NonBlankUTF8String | None, Field(alias="firmwareVersion")] = None

    # def __init__(self, make: NonBlankUTF8String | None,
    #              modelName: NonBlankUTF8String | None,
    #              serialNumber: NonBlankUTF8String | None,
    #              firmwareVersion: NonBlankUTF8String | None):
    #     super(StaticTracker, self).__init__(make=make,
    #                                         modelName=modelName,
    #                                         serialNumber=serialNumber,
    #                                         firmwareVersion=firmwareVersion)


class Tracker(CompatibleBaseModel):
    notes: tuple[NonBlankUTF8String, ...] | None = None
    recording: tuple[bool, ...] | None = None
    slate: tuple[NonBlankUTF8String, ...] | None = None
    status: tuple[NonBlankUTF8String, ...] | None = None
