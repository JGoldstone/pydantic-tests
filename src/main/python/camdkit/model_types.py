from typing import Optional, Any, Self, Annotated
from enum import Enum, StrEnum, verify, UNIQUE
from uuid import uuid4
import math

from pydantic import Field, BaseModel

from camdkit.base_types import StrictlyPositiveRational
from camdkit.backwards import CompatibleBaseModel, PODModel

class Sampling(Enum):
    STATIC = 'static'
    REGULAR = 'regular'


_SAMPLE_ID_RE_PATTERN = r'^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

# TODO re-implement these two as specializations of a generic Dimensions type
class PhysicalDimensions(CompatibleBaseModel):
    width: Annotated[float, Field(gt=0.0, lt=math.inf)]
    height: Annotated[float, Field(gt=0.0, lt=math.inf)]

    def __init__(self, width: float, height: float) -> None:
        super(PhysicalDimensions, self).__init__(width=width, height=height)


class ShutterAngle(PODModel):
    angle: Annotated[float, Field(gt=0.0, le=360.0)]

    def __init__(self, angle: float) -> None:
        super(ShutterAngle, self).__init__(angle=angle)



class SenselDimensions(BaseModel):
    width: Annotated[int, Field(gt=0)]
    height: Annotated[float, Field(gt=0)]

    def __init__(self, w: int, h: int) -> None:
        super(SenselDimensions, self).__init__(width=w, height=h)


class SampleId(PODModel):
    """Unique ID for this sample
    If no argument given when an object of this class is instantiated, a
    default value will be provided.
    If None is the sole argument, then a default value will be provided.
    If an argument is given it must be
    a valid URN of the form <insert description here>

    """
    # id: Annotated[str, Field(serialization_alias='sampleId',
    #                             pattern=_SAMPLE_ID_RE_PATTERN,
    #                             default_factory=lambda: uuid4().urn)]
    sample_id: Annotated[str, Field(alias='sampleId',
                             pattern=_SAMPLE_ID_RE_PATTERN)]

    def __init__(self, sampleId: str) -> None:
        super(SampleId, self).__init__(sampleId=sampleId)


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

@verify(UNIQUE)
class SynchronizationSource(StrEnum):
    """Synchronization sources"""

    GENLOCK = "genlock"
    VIDEO_IN = "videoIn"
    PTP = "ptp"
    NTP = "ntp"

class SynchronizationOffsets(BaseModel):
    """Synchronization offsets"""

    translation: Optional[float] = None
    rotation: Optional[float] = None
    lens_encoders: Optional[float] = None

    def __init__(self, translation: float, rotation: float, lens_encoders: float) -> None:
        super(SynchronizationOffsets, self).__init__(translation=translation,
                                                     rotation=rotation,
                                                     lens_encoders=lens_encoders)

class SynchronizationPTP(BaseModel):
    """needs better explanation"""

    domain: Optional[int] = None  # ???
    master: Optional[str] = None  # a hostname? an IPv4 address? what?
    offset: Optional[float]  # offset in what sense? and what units?

    def __init__(self, d: int, m: str, o: float) -> None:
        super(SynchronizationPTP, self).__init__(domain=d, master=m, offset=o)

class Synchronization(BaseModel):
    locked: bool
    source: SynchronizationSource
    frequency: Optional[StrictlyPositiveRational] = None
    offsets: Optional[SynchronizationOffsets] = None
    present: Optional[bool] = None
    ptp: SynchronizationPTP

