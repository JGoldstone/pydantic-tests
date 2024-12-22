#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Provisions for compatibility with OpenTrackIO 0.9 release"""

import jsonref

from typing import Any, Self

from pydantic import BaseModel, ValidationError, ConfigDict, json
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue

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

    model_config = ConfigDict(validate_assignment=True,
                              use_enum_values=True,
                              extra="forbid")

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

    @classmethod
    def make_json_schema(cls) -> json:
        with_refs = cls.model_json_schema(schema_generator=SortlessSchemaGenerator)
        without_refs = jsonref.replace_refs(with_refs, proxies=False)
        if "$defs" in without_refs:
            del without_refs["$defs"]
        return without_refs


# class RecursiveModel(BaseModel):
#     model_config = ConfigDict(validate_assignment=True,
#                               use_enum_values=True)
#
#
#     @classmethod
#     def from_json(cls, json_or_tuple: dict[str, Any] | tuple[Any, ...]) -> Any:
#         def all_keys_are_strings(d):
#             return all([type(k) == str for k in d.keys()])
#         def inner(value):  # TODO since return type is whatever cls is, can we say that?
#             # if it's a dict and all the keys are strings, let's guess it's JSON
#             is_dict: bool = isinstance(value, dict)
#             all_string_keys: bool = is_dict and all_keys_are_strings(value)
#             if is_dict and all_string_keys:
#                 result = cls.model_validate(value)
#                 print(f"base case result: {result}")
#                 return result
#             elif isinstance(value, tuple):
#                 tuple_result = tuple([inner(v) for v in value])
#                 print(f"tuple case result: {tuple_result}")
#                 return tuple_result
#             else:
#                 raise ValueError(f"unhandled type {type(value)} supplied to from_json() of {cls.__name__}")
#         print(f"about to call inner({json_or_tuple})", flush=True)
#         return inner(json_or_tuple)
#
# class Frob(RecursiveModel):
#     fred: int
#     wilma: complex
#
# def test_basic_frob_json_loads():
#     data = {"fred": 6, "wilma": 7+2j }
#     foo = Frob.from_json(data)
#     print(f"foo is ---{foo}---")
#     first_level_data = ({'fred': 1, 'wilma': 0+1j}, {'fred': 2, 'wilma': 0+2j})
#     print(f"processed tuples of data: {Frob.from_json(first_level_data)}")
#     second_level_data = (({'fred': 1, 'wilma': 0+1j}, {'fred': 2, 'wilma': 0+2j}),
#                          ({'fred': 3, 'wilma': 0+3j}, {'fred': 4, 'wilma': 0+4j}))
#     print(f"processed tuples of tuples of data: {Frob.from_json(second_level_data)}")
#
# if __name__ == '__main__':
#     test_basic_frob_json_loads()
