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
from pydantic.json_schema import JsonSchemaValue

from camdkit.camera_types import StaticCamera
from camdkit.compatibility import (property_schema_is_optional,
                                   property_schema_is_array,
                                   wrap_classic_camdkit_properties_as_optional,
                                   CompatibleBaseModel, wrap_classic_camdkit_schema_as_optional)


class PureOpt(BaseModel):
    a: int
    b: int | None = None
    c: str

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


class CompatiblePureOpt(CompatibleBaseModel):
    a: int
    b: int | None = None
    c: str

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


class AnnotatedOpt(BaseModel):
    class FauxField:
        def __init__(self, *_) -> None:
            pass

    a: int
    b: Annotated[int | None, FauxField("foo")] = None
    c: str

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


class PureArray(BaseModel):
    a: int
    b: tuple[int, ...]
    c: str

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


# regular POD parameters, e.g. lens entrance pupil offset
class OptArray(BaseModel):
    a: int
    b: tuple[int, ...] | None
    c: str

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

CLASSIC_STATIC_CAMERA_SCHEMA_W_JUST_ANAMORPHIC_SQUEEZE = {
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

STATIC_CAMERA_SCHEMA_W_JUST_ANAMORPHIC_SQUEEZE = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "anamorphicSqueeze": {
            "anyOf": [
                { "type": "object",
                  "properties": {
                      "num": { "type": "integer", "maximum": 2147483647, "minimum": 1 },
                      "denom": { "type": "integer", "maximum": 4294967295, "minimum": 1 }
                  },
                  "required": [ "num", "denom" ],
                  "additionalProperties": False },
                { "type": "null" }
            ],
            "default": None,
            "description": "Nominal ratio of height to width of the image of an axis-aligned\nsquare captured by the camera sensor. It can be used to de-squeeze\nimages but is not however an exact number over the entire captured\narea due to a lens' intrinsic analog nature.\n"
        }
    }
}


def remove_properties_besides(schema: JsonSchemaValue, keeper: str) -> JsonSchemaValue:
    property_names = [k for k in schema["properties"].keys() if k != keeper]
    for property_name in property_names:
        schema["properties"].pop(property_name)
    return schema


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

    def test_detecting_optional_anamorphic_squeeze(self):
        full_schema: dict[str, Any] = deepcopy(STATIC_CAMERA_SCHEMA_W_JUST_ANAMORPHIC_SQUEEZE)
        property_schema: dict[str, Any] = full_schema["properties"]["anamorphicSqueeze"]
        self.assertTrue(property_schema_is_optional(property_schema))

    def test_wrapping_classic_camdkit_property(self):
        with open("../resources/model/static_camera.json", "r") as file:
            classic_schema = json.load(file)
            remove_properties_besides(classic_schema, "anamorphicSqueeze")
            self.assertDictEqual(CLASSIC_STATIC_CAMERA_SCHEMA_W_JUST_ANAMORPHIC_SQUEEZE, classic_schema)
            # rewrapped_schema: JsonSchemaValue = { k: v for k, v in classic_schema.items() if k != "properties" }
            # rewrapped_schema["properties"] = wrap_classic_camdkit_properties_as_optional(classic_schema)
            rewrapped_schema = wrap_classic_camdkit_schema_as_optional(classic_schema)
            pydantic_schema = StaticCamera.make_json_schema()
            remove_properties_besides(pydantic_schema, keeper="anamorphicSqueeze")
            self.assertDictEqual(STATIC_CAMERA_SCHEMA_W_JUST_ANAMORPHIC_SQUEEZE, pydantic_schema)
            rewrapped_anam = rewrapped_schema["properties"]["anamorphicSqueeze"]
            pydantic_anam = pydantic_schema["properties"]["anamorphicSqueeze"]
            self.assertDictEqual(pydantic_anam, rewrapped_anam)
            self.assertDictEqual(pydantic_schema, rewrapped_schema)

    def test_wrapping_classic_camdkit_properties(self):
        with open("../resources/model/static_camera.json", "r") as file:
            classic_schema = json.load(file)
            rewrapped_schema = wrap_classic_camdkit_schema_as_optional(classic_schema)
            pydantic_schema = StaticCamera.make_json_schema()
            self.assertDictEqual(rewrapped_schema, pydantic_schema)


    def test_schema_for_serialization(self):
        sers = StaticCamera.make_json_schema()
        print('stop here')





    # def test_converting_pydantic_optional_schema_to_classic_schema(self):
    #     full_pydantic_schema: dict[str, Any] = deepcopy(STATIC_CAMERA_SCHEMA_W_JUST_ANAMORPHIC_SQUEEZE)
    #     pydantic_property_schema: dict[str, Any] = full_pydantic_schema["properties"]["anamorphicSqueeze"]
    #     full_classic_schema: dict[str, Any] = deepcopy(CLASSIC_STATIC_CAMERA_SCHEMA_W_JUST_ANAMORPHIC_SQUEEZE)
    #     classic_property_schema: dict[str, Any] = full_classic_schema["properties"]["anamorphicSqueeze"]
    #     self.assertNotEqual(classic_property_schema, pydantic_property_schema)
    #     convert_pydantic_optional_schema_to_classic_schema(pydantic_property_schema)
    #     self.assertEqual(classic_property_schema, pydantic_property_schema)

if __name__ == '__main__':
    unittest.main()
