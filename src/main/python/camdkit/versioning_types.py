#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for versioning protocols"""

from camdkit.compatibility import CompatibleBaseModel
from camdkit.string_types import NonBlankUTF8String

__all__ = ['OPENTRACKIO_PROTOCOL_NAME', 'VersionedProtocol']

OPENTRACKIO_PROTOCOL_NAME = "OpenTrackIO"
OPENTRACKIO_PROTOCOL_VERSION = (0, 9, 2)


class VersionedProtocol(CompatibleBaseModel):
    name: NonBlankUTF8String
    version: tuple[int, int, int]

    def __init__(self, name: NonBlankUTF8String, version: tuple[int, int, int]):
        super(VersionedProtocol, self).__init__(name=name, version=version)
        if name != OPENTRACKIO_PROTOCOL_NAME:
            raise ValueError("The only currently accepted name for a versioned protocol"
                             " is {OPENTRACKIO_PROTOCOL_NAME}")
