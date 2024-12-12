#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Provisions for compatibility with OpenTrackIO 0.9 release"""

from typing import Any
from copy import deepcopy

from pydantic import BaseModel, ValidationError, ConfigDict, json


def title_stripper(schema: dict[str, Any]) -> None:
    for prop in schema.get('properties', {}).values():
        prop.pop('title', None)
    schema.pop('title', None)

# For compatibility with existing code
class CompatibleBaseModel(BaseModel):

    model_config = ConfigDict(validate_assignment=True,
                              json_schema_extra=title_stripper)

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
        return cls.model_json_schema()

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
