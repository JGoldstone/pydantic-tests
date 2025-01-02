#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Provisions for compatibility with OpenTrackIO 0.9 release"""

import jsonref

from abc import abstractmethod
from typing import Final, Any, Self

from pydantic import BaseModel, ValidationError, ConfigDict
from pydantic.json_schema import (GenerateJsonSchema,
                                  JsonSchemaValue,
                                  JsonSchemaMode)

from pydantic_core.core_schema import ModelField

__all__ = [
    'CompatibleBaseModel',
    'BOOLEAN',
    'NONBLANK_UTF8_MAX_1023_CHARS', 'UUID_URN',
    'RATIONAL', 'STRICTLY_POSITIVE_RATIONAL',
    'NON_NEGATIVE_INTEGER', 'STRICTLY_POSITIVE_INTEGER',
    'NON_NEGATIVE_REAL', 'REAL', 'REAL_AT_LEAST_UNITY',
    'property_schema_is_optional',
    'property_schema_is_array',
    'canonicalize_descriptions'
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


def scrub_excluded(d: JsonSchemaValue, unwanted: tuple[str, ...]) -> JsonSchemaValue:
    for key, value in d.items():
        if isinstance(value, dict):
            scrub_excluded(value, unwanted)
    for key in unwanted:
        d.pop(key, None)
    return d


def canonicalize_descriptions(d: JsonSchemaValue) -> JsonSchemaValue:
    """Canonicalize docstrings into PEP8- and PEP 257-compliant form"""
    for key, value in d.items():
        if isinstance(value, dict):
            canonicalize_descriptions(value)
        if "description" in d:
            # PEP8 just says "PEP 257 describes good docstring conventions" and
            # PEP 257 has 13 paragraphs and four examples to try and explain what
            # it means (just for multiline docstrings and indentation thereof).
            # This is not the full canonicalization algorithm given in the second
            # example, but it should be enough.
            no_newlines_at_either_end: str = d["description"].strip()
            compliant = (no_newlines_at_either_end + "\n"
                         if '\n' in no_newlines_at_either_end
                         else no_newlines_at_either_end)
            d["description"] = compliant
    return d


def wrap_classic_camdkit_properties_as_optional(classic_schema: JsonSchemaValue) -> JsonSchemaValue:
    new_properties: JsonSchemaValue = {}
    properties = classic_schema["properties"]
    for prop_name, prop_value in properties.items():
        new_property: JsonSchemaValue = {}
        any_of_contents = [ {k: v for k, v in prop_value.items()
                             if k not in ("description", "units") } ,
                            { "type": "null" } ]
        new_property["anyOf"] = any_of_contents
        new_property["default"] = None
        if "description" in prop_value:
            new_property["description"] = prop_value["description"]
        if "units" in prop_value:
            new_property["units"] = prop_value["units"]
        new_properties[prop_name] = new_property
    return new_properties


def wrap_classic_camdkit_schema_as_optional(classic_schema: JsonSchemaValue) -> JsonSchemaValue:
    rewrapped_schema: JsonSchemaValue = {k: v for k, v in classic_schema.items() if k != "properties"}
    rewrapped_schema["properties"] = wrap_classic_camdkit_properties_as_optional(classic_schema)
    canonicalize_descriptions(rewrapped_schema)
    return rewrapped_schema


def property_schema_is_optional(property_schema: JsonSchemaValue) -> bool:
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

def optional_property_schema(pop_schema: JsonSchemaValue):
    return pop_schema['anyOf'][0] if property_schema_is_optional(pop_schema) else None


def property_schema_is_array(schema: JsonSchemaValue) -> bool:
    return (type(schema) is dict
            and all([name in schema for name in ('type', 'items')])
            and schema['type'] == 'array')


def array_property_schema(pap_schema: JsonSchemaValue) -> JsonSchemaValue | None:
    return pap_schema['items'] if property_schema_is_array(pap_schema) else None


class CompatibleSchemaGenerator(GenerateJsonSchema):

    def model_field_schema(self, schema: ModelField) -> JsonSchemaValue:

        def clip_property_from_schema(mf_schema: ModelField) -> str | None:
            if ('metadata' in mf_schema
                    and 'pydantic_js_extra' in mf_schema['metadata']
                    and 'clip_property' in mf_schema['metadata']['pydantic_js_extra']):
                return mf_schema['metadata']['pydantic_js_extra']['clip_property']
            return None

        def trapdoor_for_layer_type(layer_type: str):
            table = {'default': 'schema',
                     'nullable': 'schema',
                     'tuple': 'items_schema',
                     'model': 'schema',
                     # 'model': 'schema',
                     'function-before': 'schema',
                     'model-field': 'schema',
                     'model-fields': 'fields'}
            try:
                return table[layer_type]
            except KeyError as e:
                return None

        def find_layer(layer_schema: dict[str, Any],
                       sought_layer_type: str) -> dict[str, Any] | None:
            """From the given layer, descend through a series of trapdoors
            (which wiill have different names, depending on the layer)
            until we reach a layer of the sought type, and return it"""
            current_layer: dict[str, Any] = layer_schema
            while True:
                if "type" in current_layer:
                    current_layer_type = current_layer["type"]
                    if current_layer_type == sought_layer_type:
                        return current_layer
                    trapdoor = trapdoor_for_layer_type(current_layer_type)
                    if trapdoor:
                        if trapdoor in current_layer:
                            current_layer = current_layer[trapdoor]
                        else:
                            raise RuntimeError(f"schema layer of type {current_layer_type}"
                                               f" missing expected trapdoor {trapdoor}")
                    else:
                        return None
                else:
                    return None

        def remove_layer(layer_schema: dict[str, Any],
                         layer_to_be_removed) -> None:
            current_layer: dict[str, Any] = layer_schema
            while True:
                current_layer_type = current_layer["type"]
                trapdoor = trapdoor_for_layer_type(current_layer_type)
                if trapdoor:
                    if trapdoor in current_layer:
                        if current_layer == layer_to_be_removed:
                            print(f"removing layer of type {current_layer_type}")
                            layer_below = current_layer[trapdoor]
                            current_keys = list(current_layer.keys())
                            for k in current_keys:
                                current_layer.pop(k)
                            if current_layer_type == "tuple":
                                # with tuples, what we hoist up through the trapdoor to repopulate
                                # the current layer isn't in the layer below; it's in the first
                                # entry in a list in the layer below.
                                for k, v in layer_below[0].items():
                                    current_layer[k] = v
                            else:
                                for k, v in layer_below.items():
                                    current_layer[k] = v
                            return
                    else:
                        raise RuntimeError(f"schema layer of type {current_layer_type}"
                                           f" missing expected trapdoor {trapdoor}")
                    current_layer = current_layer[trapdoor]
                else:
                    raise RuntimeError(f"can't remove layer of type {current_layer_type}"
                                       f" because we don't know how to hoist up the layer"
                                       f" underneath it")

        if clip_property := clip_property_from_schema(schema):
            # if schema['metadata']['pydantic_js_extra']['clip_property'] == 'lens_raw_encoders':
            #     print('pause here')
            while True:
                removed_layer: bool = False
                if default_layer := find_layer(schema, 'default'):
                    remove_layer(schema, default_layer)
                    removed_layer = True
                if nullable_layer := find_layer(schema, 'nullable'):
                    remove_layer(schema, nullable_layer)
                    removed_layer = True
                if tuple_layer := find_layer(schema, 'tuple'):
                    remove_layer(schema, tuple_layer)
                    removed_layer = True
                # if model_fields_layer := find_layer(schema, 'model-fields'):
                #     remove_layer(schema, model_fields_layer)
                if not removed_layer:
                    break


        json_schema = super().model_field_schema(schema)
        return json_schema

    # def model_field_schema(self, schema: ModelField) -> JsonSchemaValue:
    #
    #     def is_clip_property_schema(schema: ModelField) -> bool:
    #         return ('metadata' in schema
    #                 and 'pydantic_js_extra' in schema['metadata']
    #                 and 'clip_property' in schema['metadata']['pydantic_js_extra'])
    #
    #     def find_layer(schema: ModelField, layer_type: str) -> ModelField | None:
    #         layer: ModelField = schema
    #         while True:
    #             if "type" in layer and layer["type"] == layer_type:
    #                 return layer
    #             if "schema" in layer:
    #                 layer = layer["schema"]
    #             else:
    #                 return None
    #
    #     def remove_layer(schema: ModelField, layer_to_be_removed: ModelField) -> None:
    #         current_layer = schema
    #         while True:
    #             if current_layer == layer_to_be_removed:
    #                 print(f"removing layer of type {current_layer["type"]}")
    #                 layer_below = current_layer["schema"]
    #                 current_keys = list(current_layer.keys())
    #                 for k in current_keys:
    #                     current_layer.pop(k)
    #                 for k, v in layer_below.items():
    #                     current_layer[k] = v
    #                 return
    #             if not "schema" in current_layer:
    #                 raise KeyError(f"layer {layer_to_be_removed} not found")
    #             current_layer = current_layer["schema"]
    #
    #     if is_clip_property_schema(schema):
    #         if default_layer := find_layer(schema, 'default'):
    #             if nullable_layer := find_layer(schema, 'nullable'):
    #                 remove_layer(schema, default_layer)
    #                 remove_layer(schema, nullable_layer)
    #     json_schema = super().model_field_schema(schema)
    #     return json_schema

    def sort(
            self, value: JsonSchemaValue, parent_key: str | None = None
    ) -> JsonSchemaValue:
        """No-op, we don't want to sort schema values at all."""
        return value

    @abstractmethod
    def cleanup(self, schema: JsonSchemaValue) -> None:
        raise NotImplementedError()

    def generate(self, schema: JsonSchemaValue, mode='validation'):
        json_schema = super().generate(schema, mode=mode)
        json_schema = jsonref.replace_refs(json_schema, proxies=False, merge_props=True)
        self.cleanup(json_schema)
        canonicalize_descriptions(json_schema)
        return json_schema

class InternalCompatibleSchemaGenerator(CompatibleSchemaGenerator):
    def cleanup(self, schema: JsonSchemaValue) -> None:
        scrub_excluded(schema, ALWAYS_EXCLUDED)

class ExternalCompatibleSchemaGenerator(CompatibleSchemaGenerator):
    def cleanup(self, schema: JsonSchemaValue) -> None:
        scrub_excluded(schema, ALWAYS_EXCLUDED + EXCLUDED_CAMDKIT_INTERNALS)


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
    def from_json(cls, json_or_tuple: JsonSchemaValue | tuple[Any, ...]) -> Any:
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
    def make_json_schema(cls, mode: JsonSchemaMode = 'serialization',
                         exclude_camdkit_internals: bool = True) -> JsonSchemaValue:
        schema = cls.model_json_schema(schema_generator=(ExternalCompatibleSchemaGenerator
                                                         if exclude_camdkit_internals
                                                         else InternalCompatibleSchemaGenerator),
                                       mode = mode)
        schema.pop("$defs", None)
        return schema
