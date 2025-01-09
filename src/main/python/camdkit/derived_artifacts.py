#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Provisions for compatibility with OpenTrackIO 0.9 release"""
import types
import typing

from typing import Any
from copy import deepcopy

from pydantic import BaseModel, json
from pydantic.fields import FieldInfo

from camdkit.compatibility import CompatibleBaseModel
from camdkit.string_types import NonBlankUTF8String
from camdkit.timing_types import Sampling

def summarize_constraints(field_schema: dict[str, Any]) -> str:
    if 'constraints' in field_schema:
        return field_schema['constraints']
    # some well-known cases
    #  "foo | None" turns into an 'anyOf where one of the elements is {'type': 'null'}
    #    and it's very likely there's a 'default' at the same level as 'anyOf'
    schema = deepcopy(field_schema)
    for unwanted in ('description', 'clip_property'):
        schema.pop(unwanted, None)
    if ('type' not in schema
            and 'default' in schema
            and ('anyOf' in schema and 'type' in schema['anyOf'])):
        schema.pop('default', None)
