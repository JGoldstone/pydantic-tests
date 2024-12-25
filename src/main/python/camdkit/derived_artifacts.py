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
from camdkit.timing_types import Sampling

class FieldSummary(BaseModel):
    alias: str | None = None
    description: str | None = None
    constraints: str | None = None
    sampling: Sampling = Sampling.STATIC
    section: str | None = None
    units: str | None = None

ParameterSummary = dict[str, FieldSummary]  # parameter name is key

# boolean
"""The parameter shall be a boolean."""

# UUIDURN
"""The parameter shall be a UUID URN as specified in IETF RFC 4122.
Only lowercase characters shall be used.
Example: `f81d4fae-7dec-11d0-a765-00a0c91e6bf6`
"""

# string
"""The parameter shall be a Unicode string betwee 0 and 1023
codepoints.
"""

# strictly positive rational
"""The parameter shall be a rational number whose numerator
is in the range [0..2,147,483,647] and denominator in the range
(0..4,294,967,295].
"""

# rational
"""The parameter shall be a rational number where (i) the numerator
is in the range [-2,147,483,648..2,147,483,647] and (ii) the
denominator is in the range (0..4,294,967,295].
"""

# non-negative integer
"""The parameter shall be a integer in the range (0..4,294,967,295].
"""

# strictly positive integer
"""The parameter shall be a integer in the range (1..4,294,967,295].
"""

# real
"""The parameter shall be a real number."""

# non-negative real
"""The parameter shall be a non-negative real number."""

# greater than or equal to 1
"""The parameter shall be a real number >= 1."""

# shutter angle
"""The parameter shall be a real number in the range (0..360]."""

# protocol
"""Protocol name is nonblank string; protocol version is basic x.y.z
 semantic versioning string
 """

# global stage position
"""
Each field in the GlobalPosition shall be a real number
"""

# transforms
"""Each component of each transform shall contain Real numbers."""

# dimensions
"""The height and width shall be each be real non-negative numbers.
"""

# integer dimensions
"""The height and width shall be each be an integer in the range
[0..2,147,483,647].
"""

# synchronization
"""
The parameter shall contain the required valid fields.
"""

# lens encoders
"""
The parameter shall contain at least one normalised values (0..1) for the FIZ encoders.
"""

# lens raw encoders
"""
The parameter shall contain at least one integer value for the FIZ encoders.
"""

# timestamp
"""The parameter shall contain valid number of seconds, nanoseconds
elapsed since the start of the epoch.
"""

# timecode
"""The parameter shall contain a valid format and hours, minutes,
seconds and frames with appropriate min/max values.
"""

# exposure falloff
"""The coefficients shall each be real numbers."""

# distortions
# undistortions
"""The list shall contain at least one Distortion object, and in each
object the radial and tangential coefficients shall each be real numbers.
"""

# lens distortion offset
"""X and Y centre shift shall each be real numbers."""

# lens projector offset
"""X and Y projection offset shall each be real numbers."""



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

#

#     # get rid of description
# # get rid of property
# # get rid of default
# # is there a 'type' left?
# # is there an anyOf that has one entry that is not 'type': 'null'?
#     if field_type not in ('str', 'int', 'float', 'bool'):
#
# def summarize_field(model_class: type[Any],
#                     model_schema:dict[str, Any],
#                     field_name: str) -> FieldSummary:
#     summary = FieldSummary()
#     model_name: str = model_class.__name__
#     summary.sampling = Sampling.STATIC if model_name.startswith("Static") else Sampling.REGULAR
#     section = model_name.lstrip("Static").lower()
#     if section == "Clip":
#         section = None
#         summary.section = section
#     field_schema: dict[str, Any] = model_schema[field_name]
#     if 'units' in field_schema:
#         summary.units = field_schema['units']
#
#
#
#
#
#     try:
#         field_dict = model_schema["properties"]
#     except KeyError:
#         raise ValueError()


def sole_non_none_type_from_union_type(t: type[Any]) -> type[Any]:
    if not isinstance(t, types.UnionType):
        raise ValueError(f"{t} is not a union type")
    allowed_types = typing.get_args(t)
    if len(allowed_types) != 2:
        raise ValueError(f"{t} should have two possible types, of which one is None,"
                         f" but it has {len(allowed_types)}: {allowed_types}")
    if not types.NoneType in allowed_types:
        raise ValueError(f"{t} should have two possible types, of which one is None,"
                         f" but None wasn't in: {allowed_types}")
    # we rely on the type system to ensure NoneType isn't in there twice
    return allowed_types[0] if allowed_types[0] else allowed_types[1]

def tuple_type_and_field_info(tuple_type) -> tuple[type[Any], FieldInfo | None]:
    tuple_generic_type_args = typing.get_args(tuple_type)
    if tuple_generic_type_args:
        # remove any trailing ellipsis
        if tuple_generic_type_args[-1] == Ellipsis:
            tuple_generic_type_args = tuple_generic_type_args[:-1]
        if len(tuple_generic_type_args) == 1:  # not fully general but enough for camdkit
            base_info = tuple_generic_type_args[0]
            if isinstance(base_info, tuple):
                base_type, field_info = base_info
                return base_type, field_info
            else:  # it's just a tuple[<pod>] or tuple[<pod>, ...] most likely
                return base_info, None
        else:
            raise NotImplementedError(f"multi-type tuples not implemented yet for {tuple_generic_type_args}")
    else:
        raise ValueError(f"supplied tuple type is not a subclass of a generic tuple type")

def make_parameter_doc(field: str,
                       container_name: str,
                       field_info: FieldInfo) -> tuple[str, FieldSummary]:
    sampling: Sampling = (Sampling.STATIC
                          if container_name == "static" or container_name is None
                          else Sampling.REGULAR)

def traverse_model_fields(root_type: type[Any],
                          container_name: str,
                          params: ParameterSummary) -> None:
    def inner(model_type: type[Any], indent=0):
        assert issubclass(model_type, CompatibleBaseModel)
        print(f"{' '*indent}CompatibleBaseModel is {str(model_type)} with"
              f" {len(model_type.model_fields) if model_type.model_fields else "no"}"
              f" model fields")
        # print(f"there are {len(model_type.__pydantic_fields__)} pydantic fields")
        for field, field_info in model_type.model_fields.items():
            field_type = field_info.annotation
            if typing.get_origin(field_type) == types.UnionType:
                field_type = sole_non_none_type_from_union_type(field_type)
            print(f"{' '*indent}field {field} has type {field_type}")
            if typing.get_origin(field_type) == tuple:
                elem_type, field_info = tuple_type_and_field_info(field_type)
                if issubclass(elem_type, CompatibleBaseModel):
                    inner(elem_type, indent + 4)
                else:
                    params[field] = make_parameter_doc(field_type, field_info)
                    print(f"{' '*indent}field {field} is a tuple of type {elem_type} with info {field_info}")
            elif isinstance(field_type, typing.TypeAliasType):
                print(f"{' '*indent}skipping {field} as it's a type alias, don't know how to handle it")
            elif issubclass(field_type, CompatibleBaseModel):
                inner(field_type, indent + 4)
            if field not in params:
                params[field] = field_type
    inner(root_type)