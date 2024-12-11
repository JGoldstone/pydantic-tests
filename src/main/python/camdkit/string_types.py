#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling constrained strings"""

from typing import Annotated

from pydantic import Field, StringConstraints

__all__ = ['NonBlankUTF8String', 'UUIDURN']

type NonBlankUTF8String = Annotated[str, StringConstraints(min_length=1, max_length=1023)]

UUID_URN_PATTERN = r'^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

type UUIDURN = Annotated[str, Field(pattern=UUID_URN_PATTERN)]
