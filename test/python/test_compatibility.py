#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Tests for components providing compatibility with classic camdkit"""

import unittest
import json

from typing import Annotated, Any
from copy import deepcopy

from pydantic import BaseModel

from camdkit.compatibility import (property_schema_is_optional,
                                   property_schema_is_array,
                                   CompatibleBaseModel)

EXPECTED_PURE_OPT_SCHEMA = {
    # n.b. dict order changed from BaseModel.model_json_schema() output to be sure that
    #   order of elements isn't important
    "type": "object",
    "properties": {
        "a": { "title": "A", "type": "integer" },
        "b": { "anyOf": [ { "type": "integer" }, { "type": "null" } ],
               "default": None, "title": "B" },
        "c": { "title": "C", "type": "string" }
    },
    "required": [ "a", "c" ],
    "title": "PureOpt"
}

EXPECTED_COMPATIBLE_PURE_OPT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "a": { "type": "integer" },
        "b": { "anyOf": [ { "type": "integer" }, { "type": "null" } ],
               "default": None },
        "c": { "type": "string" }
    },
    "required": [ "a", "c" ]
}

EXPECTED_ANNOTATED_OPT_SCHEMA = {
    "type": "object",
    "properties": {
        "a": { "title": "A", "type": "integer" },
        "b": { "anyOf": [ { "type": "integer" }, { "type": "null" } ],
               "default": None, "title": "B" },
        "c": { "title": "C", "type": "string" }
    },
    "required": [ "a", "c" ],
    "title": "AnnotatedOpt"
}

EXPECTED_PURE_ARRAY_SCHEMA = {
    "properties": {
        "a": { "title": "A", "type": "integer" },
        "b": { "title": "B",
               "type": "array",
               "items": {"type": "integer" } },
        "c": { "title": "C", "type": "string" }
    },
    "required": [ "a", "b", "c" ],
    "title": "PureArray",
    "type": "object"
}

EXPECTED_OPT_ARRAY_SCHEMA = {
    "properties": {
        "a": { "title": "A", "type": "integer" },
        "b": { "title": "B",
               "anyOf": [
                   { "items": { "type": "integer" }, "type": "array" },
                   { "type": "null" } ] },
        "c": { "title": "C", "type": "string" }
    },
    "required": [ "a", "b", "c" ],
    "title": "OptArray",
    "type": "object"
}

CLASSIC_CAMERA_ANAMORPHIC_SQUEEZE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "anamorphicSqueeze": {
            "type": "object",
            "properties": {
                "num": { "type": "integer", "minimum": 1, "maximum": 2147483647 },
                "denom": { "type": "integer", "minimum": 1, "maximum": 4294967295 } },
            "required": [ "num", "denom" ],
            "additionalProperties": False,
            "description": "Nominal ratio of height to width of the image of an axis-aligned\nsquare captured by the camera sensor. It can be used to de-squeeze\nimages but is not however an exact number over the entire captured\narea due to a lens' intrinsic analog nature.\n"
        },
    }
}


PYDANTIC_CAMERA_ANAMORPHIC_SQUEEZE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "anamorphicSqueeze": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "num": { "type": "integer", "minimum": 1, "maximum": 2147483647 },
                        "denom": { "type": "integer", "minimum": 1, "maximum": 4294967295 } },
                    "required": [ "num", "denom" ],
                    "additionalProperties": False,
                    "description": "Nominal ratio of height to width of the image of an axis-aligned\nsquare captured by the camera sensor. It can be used to de-squeeze\nimages but is not however an exact number over the entire captured\narea due to a lens' intrinsic analog nature.\n"
                },
                { "type": "null" }
            ],
            "default": None
        }
    },
    "description": "camera properties that do not change over time\n"
}


class PureOpt(BaseModel):
    a: int
    b: int | None = None
    c: str


class CompatiblePureOpt(CompatibleBaseModel):
    a: int
    b: int | None = None
    c: str


class AnnotatedOpt(BaseModel):
    class FauxField:
        def __init__(self, *_) -> None:
            pass
    a: int
    b: Annotated[int | None,  FauxField("foo")] = None
    c: str

class PureArray(BaseModel):
    a: int
    b: tuple[int, ...]
    c: str

# regular POD parameters, e.g. lens entrance pupil offset
class OptArray(BaseModel):
    a: int
    b: tuple[int, ...] | None
    c: str


class CompatibilityTestCases(unittest.TestCase):
    # make sure Pydantic hasn't changed its schema generator without our noticing
    def test_schema_generation(self):
        self.assertDictEqual(EXPECTED_PURE_OPT_SCHEMA, PureOpt.model_json_schema())
        self.assertDictEqual(EXPECTED_COMPATIBLE_PURE_OPT_SCHEMA, CompatiblePureOpt.make_json_schema())
        self.assertDictEqual(EXPECTED_COMPATIBLE_PURE_OPT_SCHEMA, CompatiblePureOpt.make_json_schema())
        self.assertDictEqual(EXPECTED_ANNOTATED_OPT_SCHEMA, AnnotatedOpt.model_json_schema())
        self.assertDictEqual(EXPECTED_PURE_ARRAY_SCHEMA, PureArray.model_json_schema())
        self.assertDictEqual(EXPECTED_OPT_ARRAY_SCHEMA, OptArray.model_json_schema())

    def test_annotated_opt_same_as_pure_opt(self):
        """Convince ourselves Annotated leaves no trace in generated schema"""
        pure_opt_schema = PureOpt.model_json_schema()
        annotated_opt_schema = AnnotatedOpt.model_json_schema()
        pure_opt_schema.pop("title", None)
        annotated_opt_schema.pop("title", None)
        self.assertDictEqual(pure_opt_schema, annotated_opt_schema)

    def test_detecting_optional_schema_property(self):
        """detect Pydantic-generated property schema for <var>: <type> | None """
        pure_opt_schema = PureOpt.model_json_schema()
        self.assertTrue(property_schema_is_optional(pure_opt_schema["properties"]["b"]))
        self.assertFalse(property_schema_is_optional((pure_opt_schema["properties"]["b"],)))
        no_any_of: dict[str, Any] = deepcopy(EXPECTED_PURE_OPT_SCHEMA)
        no_any_of["properties"]["b"] = { "title": "B", "type": "boolean", "default": True }
        self.assertFalse(property_schema_is_optional(no_any_of))
        no_default: dict[str, Any] = deepcopy(EXPECTED_PURE_OPT_SCHEMA)
        no_default["properties"]["b"] = { "title": "B", "anyOf": [ {"type": "integer"}, {"type": "null"} ] }
        self.assertFalse(property_schema_is_optional(no_default))
        any_of_is_not_list: dict[str, Any] = deepcopy(EXPECTED_PURE_OPT_SCHEMA)
        any_of_is_not_list["properties"]["b"]["anyOf"] = "foo"
        self.assertFalse(property_schema_is_optional(any_of_is_not_list))
        any_of_list_is_too_small: dict[str, Any] = deepcopy(EXPECTED_PURE_OPT_SCHEMA)
        any_of_list_is_too_small["properties"]["b"]["anyOf"] = any_of_list_is_too_small["properties"]["b"]["anyOf"][:1]
        self.assertFalse(property_schema_is_optional(any_of_list_is_too_small))
        any_of_list_is_too_long: dict[str, Any] = deepcopy(EXPECTED_PURE_OPT_SCHEMA)
        any_of_list_is_too_long["properties"]["b"]["anyOf"].append({"foo": "bar"})
        self.assertFalse(property_schema_is_optional(any_of_list_is_too_long))
        any_of_list_first_elem_not_dict: dict[str, Any] = deepcopy(EXPECTED_PURE_OPT_SCHEMA)
        any_of_list_first_elem_not_dict["properties"]["b"][0] = "foo"
        self.assertFalse(property_schema_is_optional(any_of_list_first_elem_not_dict))
        any_of_first_item_missing_type = deepcopy(EXPECTED_PURE_OPT_SCHEMA)
        any_of_first_item_missing_type["properties"]["b"]["anyOf"][0].pop("item", None)
        self.assertFalse(property_schema_is_optional(any_of_first_item_missing_type))
        any_of_first_item_unsupported_type = deepcopy(EXPECTED_PURE_OPT_SCHEMA)
        any_of_first_item_unsupported_type["properties"]["b"]["anyOf"][0]["type"] = complex
        self.assertFalse(property_schema_is_optional(any_of_first_item_unsupported_type))

    def test_detecting_optional_anamorphic_squeeze(self):
        full_schema: dict[str, Any] = deepcopy(PYDANTIC_CAMERA_ANAMORPHIC_SQUEEZE_SCHEMA)
        property_schema: dict[str, Any] = full_schema["properties"]["anamorphicSqueeze"]
        self.assertTrue(property_schema_is_optional(property_schema))

    # def test_converting_pydantic_optional_schema_to_classic_schema(self):
    #     full_pydantic_schema: dict[str, Any] = deepcopy(PYDANTIC_CAMERA_ANAMORPHIC_SQUEEZE_SCHEMA)
    #     pydantic_property_schema: dict[str, Any] = full_pydantic_schema["properties"]["anamorphicSqueeze"]
    #     full_classic_schema: dict[str, Any] = deepcopy(CLASSIC_CAMERA_ANAMORPHIC_SQUEEZE_SCHEMA)
    #     classic_property_schema: dict[str, Any] = full_classic_schema["properties"]["anamorphicSqueeze"]
    #     self.assertNotEqual(classic_property_schema, pydantic_property_schema)
    #     convert_pydantic_optional_schema_to_classic_schema(pydantic_property_schema)
    #     self.assertEqual(classic_property_schema, pydantic_property_schema)

    def test_detecting_array_schema_property(self):
        """detect Pydantic-generated property schema for <var>: tuple[<type>, ...]"""
        pure_array_schema = PureArray.model_json_schema()
        self.assertTrue(property_schema_is_array(pure_array_schema["properties"]["b"]))
        self.assertFalse(property_schema_is_array((pure_array_schema["properties"]["b"],)))
        no_items: dict[str, Any] = deepcopy(EXPECTED_PURE_ARRAY_SCHEMA)
        no_items["properties"]["b"].pop("items", None)
        self.assertFalse(property_schema_is_array(no_items))
        no_type: dict[str, Any] = deepcopy(EXPECTED_PURE_ARRAY_SCHEMA)
        no_type["properties"]["b"].pop("type", None)
        self.assertFalse(property_schema_is_array(no_type))
        type_is_not_array: dict[str, Any] = deepcopy(EXPECTED_PURE_ARRAY_SCHEMA)
        type_is_not_array["properties"]["b"]["type"] = "string"
        self.assertFalse(property_schema_is_array(no_type))

if __name__ == '__main__':
    unittest.main()
