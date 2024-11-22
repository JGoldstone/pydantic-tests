from typing import Optional, Any, Self, Annotated
from enum import Enum
from uuid import uuid4

from pydantic import Field, BaseModel

from camdkit.base_types import StrictlyPositiveRational


class Sampling(Enum):
    STATIC = 'static'
    REGULAR = 'regular'


_SAMPLE_ID_RE_PATTERN = r'^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

# The below is simple to use in APIs and as fields in a BaseModel
# subclass, but not straightforward to validate in isolation,
# which is something we want. One can use a TypeAdapter but apparently
# then you can't use it in a basemodel...


class SampleId(BaseModel):
    value: Annotated[str, Field(alias='sampleId',
                                pattern=_SAMPLE_ID_RE_PATTERN,
                                default_factory=lambda: uuid4().urn)]
    canonical_name: str = "sampleId"
    sampling: Sampling = Sampling.REGULAR
    units: Optional[str] = None

    def validate(self):
        type(self).model_validate(self)

    def to_json(self, indent: Optional[int] = None) -> dict[str, Any]:
        return self.model_dump(by_alias=True,
                               exclude={'canonical_name',
                                        'sampling',
                                        'units',
                                        'section'})

    def from_json(self, json_dict: dict[str, Any]) -> Self:
        return FrameRate(**json_dict)

    def json_schema(self) -> dict[str, Any]:
        return FrameRate.model_json_schema()


class FrameRate(StrictlyPositiveRational):
    canonical_name: str = 'captureRate'
    sampling: Sampling = Sampling.REGULAR
    units: str = "hertz"
    section: str = "camera"

    def validate(self):
        type(self).model_validate(self)

    def to_json(self, indent: Optional[int] = None) -> dict[str, Any]:
        return self.model_dump(exclude={'canonical_name',
                                 'sampling',
                                 'units',
                                 'section'})

    def from_json(self, json_dict: dict[str, Any]) -> Self:
        return FrameRate(**json_dict)

    def json_schema(self) -> dict[str, Any]:
        return FrameRate.model_json_schema()