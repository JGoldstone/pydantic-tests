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
    'NON_NEGATIVE_REAL', 'REAL', 'REAL_AT_LEAST_UNITY',
    'property_schema_is_optional',
    'property_schema_is_array'
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

# Attributes of parameters that should be culled from any exported property_schema
ALWAYS_EXCLUDED = ("title",)
EXCLUDED_CAMDKIT_INTERNALS = ("clip_property", "constraints")


def scrub_excluded(d: dict[str, Any], unwanted: tuple[str, ...]) -> dict[str, Any]:
    for key, value in d.items():
        if isinstance(value, dict):
            scrub_excluded(value, unwanted)
    for key in unwanted:
        d.pop(key, None)
    return d

def append_newlines_to_descriptions(d: dict[str, Any]) -> dict[str, Any]:
    for key, value in d.items():
        if isinstance(value, dict):
            append_newlines_to_descriptions(value)
        # TODO: the endswith() thing is a horrible hack. Fix this cleanly.
        if "description" in d and not d["description"].endswith("\n"):
            d["description"] = d["description"] + "\n"
    return d

# def copy_description_property_down(prop_name, prop_schema) -> dict[str, Any]:
#     result: dict[str, Any] = {'copied': False}
#     levels_transited: list[str] = []
#     if "description" in prop_schema:
#         # print(f"attempting to move 'description' downwards from {prop_name}")
#         target_schema = prop_schema
#         while property_schema_is_optional(target_schema) or property_schema_is_array(target_schema):
#             if property_schema_is_optional(target_schema):
#                 target_schema = target_schema['anyOf'][0]
#                 levels_transited.append("optional")
#             if property_schema_is_array(target_schema):
#                 target_schema = target_schema['items']
#                 levels_transited.append("array")
#         if target_schema is not prop_schema:
#             # target_schema['description'] = prop_schema['description']
#             result['copied'] = True
#         # if levels_transited:
#         #     print(f"moved description property through {levels_transited}")
#     return result

# def remove_copied_description_property(prop_name,
#                                        prop_schema,
#                                        prior_result: dict[str, Any]) -> None:
#     if "description" in prop_schema and "copied" in prior_result and prior_result["copied"]:
#         # print(f"attempting to delete original description property from '{prop_name}'")
#         del prop_schema["description"]

# def convert_pydantic_optional_schema_to_classic_schema(_: str, prop_schema: dict[str, Any]) -> None:
#     inner_schema = [d for d in prop_schema["anyOf"] if d != {"type": "null"}][0]
#     prop_schema |= inner_schema
#     prop_schema.pop("anyOf")
#     prop_schema.pop("default")
#     print('done')

def property_schema_is_optional(property_schema: dict[str, Any]) -> bool:
    """Detect Pydantic-generated chunk of schema corresponding to an optional property."""
    return (type(property_schema) is dict
            # and 2 <= len(property_schema) <= 3
            and all([name in property_schema for name in ('anyOf', 'default')])
            and isinstance(property_schema['anyOf'], list)
            and len(property_schema['anyOf']) == 2
            and isinstance(property_schema['anyOf'][0], dict)
            and (('type' in property_schema['anyOf'][0]
                  and property_schema['anyOf'][0]['type'] in ('object', 'array', 'string',
                                                              'number', 'boolean', 'integer'))
                 or '$ref' in property_schema['anyOf'][0])
            )

def optional_property_schema(pop_schema: dict[str, Any]):
    return pop_schema['anyOf'][0] if property_schema_is_optional(pop_schema) else None

def property_schema_is_array(schema: dict[str, Any]) -> bool:
    return (type(schema) is dict
            and all([name in schema for name in ('type', 'items')])
            and schema['type'] == 'array')

def array_property_schema(pap_schema: dict[str, Any]) -> dict[str, Any] | None:
    return pap_schema['items'] if property_schema_is_array(pap_schema) else None

# def walk_schema(parent_name: str | None,
#                 schema: dict[str, Any],
#                 indent: int = 0,
#                 opt_param_pre_walk_fn: Callable = lambda *args: None,
#                 opt_param_post_walk_fn: Callable = lambda *args: None,
#                 array_param_pre_walk_fn: Callable = lambda *args: None,
#                 array_param_post_walk_fn: Callable = lambda *args: None) -> None:
#     if isinstance(schema, dict) and "type" in schema and schema["type"] == "object":
#         if "properties" in schema and type(schema["properties"]) is dict:
#             for prop_name, prop_value in schema["properties"].items():
#                 # optional parameters interpose a layer of indirection we want to jump over
#                 # be careful to not modify schema["properties"] while we are iterating over it
#                 if opt_param_schema := optional_property_schema(prop_value):
#                     # pre_opt_walk_result: dict[str, Any] = opt_param_pre_walk_fn(prop_name, prop_value)
#                     pre_opt_walk_result = {}
#                     walk_schema(prop_name,
#                                 opt_param_schema,
#                                 indent = indent + 2,
#                                 opt_param_pre_walk_fn=opt_param_pre_walk_fn,
#                                 opt_param_post_walk_fn=opt_param_post_walk_fn,
#                                 array_param_pre_walk_fn=array_param_pre_walk_fn,
#                                 array_param_post_walk_fn=array_param_post_walk_fn)
#                     opt_param_post_walk_fn(prop_name, prop_value, pre_opt_walk_result)
#                 if array_param_schema := array_property_schema(prop_value):
#                     pre_array_walk_result = array_param_pre_walk_fn(prop_name, array_param_schema)
#                     walk_schema(prop_name,
#                                 opt_param_schema,
#                                 indent=indent + 2,
#                                 opt_param_pre_walk_fn=opt_param_pre_walk_fn,
#                                 opt_param_post_walk_fn=opt_param_post_walk_fn,
#                                 array_param_pre_walk_fn=array_param_pre_walk_fn,
#                                 array_param_post_walk_fn=array_param_post_walk_fn)
#                     array_param_post_walk_fn(prop_name, array_param_schema, pre_array_walk_result)
#
# def move_definitions_inside_arrays(schema: dict[str, Any]) -> None:
#     walk_schema(parent_name=None, schema=schema, indent=2,
#                 opt_param_pre_walk_fn=copy_description_property_down,
#                 opt_param_post_walk_fn=remove_copied_description_property,
#                 array_param_pre_walk_fn=copy_description_property_down,
#                 array_param_post_walk_fn=remove_copied_description_property)
#
# def remove_pydantic_anyof_structure(schema: dict[str, Any]) -> None:
#     walk_schema(parent_name=None, schema=schema, indent=2,
#                 opt_param_pre_walk_fn=convert_pydantic_optional_schema_to_classic_schema)



class CompatibleSchemaGenerator(GenerateJsonSchema):

    def sort(
            self, value: JsonSchemaValue, parent_key: str | None = None
    ) -> JsonSchemaValue:
        """No-op, we don't want to sort schema values at all."""
        return value

    def cleanup(self, schema: dict[str, Any]) -> None:
        pass

    def generate(self, schema, mode='validation'):
        json_schema = super().generate(schema, mode=mode)
        json_schema = jsonref.replace_refs(json_schema, proxies=False, merge_props=True)
        self.cleanup(json_schema)
        append_newlines_to_descriptions(json_schema)
        return json_schema

class InternalCompatibleSchemaGenerator(CompatibleSchemaGenerator):
    def cleanup(self, schema: dict[str, Any]) -> None:
        scrub_excluded(schema, ALWAYS_EXCLUDED)

class ExternalCompatibleSchemaGenerator(CompatibleSchemaGenerator):
    def cleanup(self, schema: dict[str, Any]) -> None:
        scrub_excluded(schema, ALWAYS_EXCLUDED + EXCLUDED_CAMDKIT_INTERNALS)

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

    @classmethod
    def make_json_schema(cls, exclude_camdkit_internals: bool = True) -> json:
        schema = cls.model_json_schema(schema_generator=(ExternalCompatibleSchemaGenerator
                                                         if exclude_camdkit_internals
                                                         else InternalCompatibleSchemaGenerator))
        schema.pop("$defs", None)
        return schema
