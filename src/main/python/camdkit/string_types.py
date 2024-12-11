#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling constrained strings"""

from typing import Annotated

from pydantic import StringConstraints

__all__ = ['NonBlankUTF8String']

type NonBlankUTF8String = Annotated[str, StringConstraints(min_length=1, max_length=1023)]
