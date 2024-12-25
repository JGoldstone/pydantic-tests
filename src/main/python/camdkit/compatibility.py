#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Provisions for compatibility with OpenTrackIO 0.9 release"""

import jsonref

from typing import Final, Any, Self

from pydantic import BaseModel, ValidationError, ConfigDict, json
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue

__all__ = [
    'CompatibleBaseModel',
    'BOOLEAN',
    'NONBLANK_UTF8_MAX_1023_CHARS', 'UUID_URN',
    'RATIONAL', 'STRICTLY_POSITIVE_RATIONAL',
    'NON_NEGATIVE_INTEGER', 'STRICTLY_POSITIVE_INTEGER',
    'NON_NEGATIVE_REAL', 'REAL', 'REAL_AT_LEAST_UNITY'
]

BOOLEAN: Final[str] = """The parameter shall be a boolean."""

NONBLANK_UTF8_MAX_1023_CHARS: Final[str] = \
"""The parameter shall be a Unicode string betwee 0 and 1023
codepoints.
"""

UUID_URN: Final[str] = \
    """The parameter shall be a UUID URN as specified in IETF RFC 4122.
    Only lowercase characters shall be used.
    Example: `f81d4fae-7dec-11d0-a765-00a0c91e6bf6`
    """

RATIONAL: Final[str] = \
    """The parameter shall be a rational number where (i) the numerator
    is in the range [-2,147,483,648..2,147,483,647] and (ii) the
    denominator is in the range (0..4,294,967,295].
    """

STRICTLY_POSITIVE_RATIONAL: Final[str] = \
    """The parameter shall be a rational number whose numerator
    is in the range [0..2,147,483,647] and denominator in the range
    (0..4,294,967,295].
    """

NON_NEGATIVE_INTEGER: Final[str] = \
    """The parameter shall be a integer in the range (0..4,294,967,295].
    """

STRICTLY_POSITIVE_INTEGER: Final[str] = \
    """The parameter shall be a integer in the range (1..4,294,967,295].
    """

REAL: Final[str] = \
    """The parameter shall be a real number."""

NON_NEGATIVE_REAL: Final[str] = \
    """The parameter shall be a non-negative real number."""

REAL_AT_LEAST_UNITY: Final[str]= \
    """The parameter shall be a real number >= 1."""

PARAMETER_CONSTRAINTS = {
    'active_sensor_physical_dimensions': """The height and width shall be each be real non-negative numbers.
""",
    'active_sensor_resolution': """The height and width shall be each be an integer in the range
[0..2,147,483,647].
""",
    "camera_make": NONBLANK_UTF8_MAX_1023_CHARS,
    "camera_model": NONBLANK_UTF8_MAX_1023_CHARS,
    "camera_serial_number": NONBLANK_UTF8_MAX_1023_CHARS,
    "camera_firmware_version": NONBLANK_UTF8_MAX_1023_CHARS,
    "camera_label": NONBLANK_UTF8_MAX_1023_CHARS,
    "anamorphic_squeeze": STRICTLY_POSITIVE_RATIONAL,
    "iso": STRICTLY_POSITIVE_INTEGER,

}
def scrub_titles(d: dict[str, Any]) -> dict[str, Any]:
    for key, value in d.items():
        if isinstance(value, dict):
            scrub_titles(value)
    if 'title' in d:
        d.pop('title')
    return d

def append_newlines_to_descriptions(d: dict[str, Any]) -> dict[str, Any]:
    for key, value in d.items():
        if isinstance(value, dict):
            append_newlines_to_descriptions(value)
        # TODO: the endswith() thing is a horrible hack. Fix this cleanly.
        if "description" in d and not d["description"].endswith("\n"):
            d["description"] = d["description"] + "\n"
    return d

class SortlessSchemaGenerator(GenerateJsonSchema):

    def generate(self, schema, mode='validation'):
        json_schema = super().generate(schema, mode=mode)
        json_schema = jsonref.replace_refs(json_schema, proxies=False)
        scrub_titles(json_schema)
        append_newlines_to_descriptions(json_schema)
        return json_schema

    def sort(
        self, value: JsonSchemaValue, parent_key: str | None = None
    ) -> JsonSchemaValue:
        """No-op, we don't want to sort schema values at all."""
        return value

def compatibility_cleanups(schema: dict[str, Any]) -> None:
    if 'description' in schema:
        # Pydantic strips away the final newline, but classic camdkit does not.
        schema["description"] = schema["description"] + "\n"

# For compatibility with existing code
class CompatibleBaseModel(BaseModel):
    """Base class for all camdkit parameters."""

    model_config = ConfigDict(validate_assignment=True,
                              use_enum_values=True,
                              extra="forbid",
                              use_attribute_docstrings=True)

    @classmethod
    def validate(cls, value:Any) -> bool:
        try:
            cls.model_validate(value)
            return True
        except ValidationError:
            return False

    # @staticmethod
    # def to_json(value: Any) -> json:
    #     return value.model_dump(by_alias=True,
    #                             exclude_none=True,
    #                             exclude={"canonical_name",
    #                                      "sampling",
    #                                      "units",
    #                                      "section"})

    @classmethod
    def to_json(cls, model_or_tuple: Self | tuple):
        def inner(one_or_many: Self | tuple):
            # TODO figure out how to express isinstance(one_or_many, CompatibleBaseModel)
            #   despite the fact that we aren't done defining it yet
            if isinstance(one_or_many, BaseModel):
                return one_or_many.model_dump(by_alias=True,
                                                exclude_none=True,
                                                exclude={"canonical_name",
                                                         "sampling",
                                                         "units",
                                                         "section"})
            if isinstance(one_or_many, tuple):
                return tuple([inner(e) for e in one_or_many])
            raise ValueError(f"unhandled object handed to {cls.__name__}.to_json()")
        return inner(model_or_tuple)

    # @classmethod
    # def from_json(cls, json_data: json) -> Any:
    #     return cls.model_validate(json_data)

    @classmethod
    def from_json(cls, json_or_tuple: dict[str, Any] | tuple[Any, ...]) -> Any:
        """Return a validated object from a JSON dict, or tuple of validated objects
        from a tuple of JSON dicts, or a tuple of tuples of validated objects from
        a tuple of tuples of JSON dicts, or ... it's basically JSON all the way down
        """
        def inner(value):  # TODO since return type is whatever cls is, can we say that?
            if isinstance(value, dict) and all([type(k) == str for k in value.keys()]):
                return cls.model_validate(value)
            elif isinstance(value, tuple):
                return tuple([inner(v) for v in value])
            else:
                raise ValueError(f"unhandled type {type(value)} supplied to"
                                 f" {cls.__name__}.from_json()")
        return inner(json_or_tuple)

    # @classmethod
    # def make_json_schema(cls) -> json:
    #     with_refs = cls.model_json_schema(schema_generator=SortlessSchemaGenerator)
    #     without_refs = jsonref.replace_refs(with_refs, proxies=False)
    #     if "$defs" in without_refs:
    #         del without_refs["$defs"]
    #     return without_refs

    @classmethod
    def make_json_schema(cls) -> json:
        schema = cls.model_json_schema(schema_generator=SortlessSchemaGenerator)
        if "$defs" in schema:
            del schema["$defs"]
        return schema
