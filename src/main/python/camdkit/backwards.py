#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Provisions for compatibility with OpenTrackIO 0.9 release"""

import jsonref

from typing import Any
from copy import deepcopy

from pydantic import BaseModel, ValidationError, ConfigDict, json
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue

class SortlessSchemaGenerator(GenerateJsonSchema):
    def sort(
        self, value: JsonSchemaValue, parent_key: str | None = None
    ) -> JsonSchemaValue:
        """No-op, we don't want to sort schema values at all."""
        return value

def title_stripper(schema: dict[str, Any]) -> None:
    for prop in schema.get('properties', {}).values():
        prop.pop('title', None)
    schema.pop('title', None)

# For compatibility with existing code
class CompatibleBaseModel(BaseModel):

    model_config = ConfigDict(validate_assignment=True,
                              use_enum_values=True,
                              json_schema_extra=title_stripper,
                              extra="forbid")

    @classmethod
    def validate(cls, value) -> bool:
        try:
            cls.model_validate(value)
            return True
        except ValidationError:
            return False

    def to_json(self, *_) -> json:
        return self.model_dump(by_alias=True,
                               exclude={"canonical_name",
                                        "sampling",
                                        "units",
                                        "section"})

    @classmethod
    def from_json(cls, json_data: json) -> Any:
        return cls.model_validate(json_data)

    @classmethod
    def make_json_schema(cls) -> json:
        with_refs = cls.model_json_schema(schema_generator=SortlessSchemaGenerator)
        without_refs = jsonref.replace_refs(with_refs, proxies=False)
        if "$defs" in without_refs:
            del without_refs["$defs"]
        return without_refs

def scrub_title(json_data: json) -> json:
    if "title" in json_data:
        del json_data["title"]
    return json_data

def hoist_pod_and_scrub_title(json) -> None:
    assert(len(json["properties"]) == 1)
    pod_name = list(json["properties"].keys())[0]
    pod_json =  deepcopy(json["properties"][pod_name])  # probably overkill
    json.clear()
    for k, v in scrub_title(pod_json).items():
        json[k] = v
