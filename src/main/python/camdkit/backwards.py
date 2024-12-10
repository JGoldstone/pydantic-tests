
from typing import Any
from copy import deepcopy

from pydantic import BaseModel, ValidationError, ConfigDict, json

# For compatibility with existing code
class CompatibleBaseModel(BaseModel):

    @classmethod
    def validate(cls, value) -> bool:
        try:
            cls.model_validate(value)
            return True
        except ValidationError:
            return False

    @staticmethod
    def to_json(value: Any) -> json:
        return value.model_dump(by_alias=True,
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


class PODModel(CompatibleBaseModel):
    model_config = ConfigDict(json_schema_extra=hoist_pod_and_scrub_title)

