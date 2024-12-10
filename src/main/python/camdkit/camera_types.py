import math

from typing import Annotated, Optional

from pydantic import Field

from camdkit.backwards import CompatibleBaseModel, PODModel
from camdkit.base_types import (NonBlankUTF8String,
                                StrictlyPositiveInt,
                                StrictlyPositiveRational)
from camdkit.model_types import UUIDURN


# Tempting as it might seem to make PhysicalDimensions and SenselDimensions subclasses
# of a single generic Dimension[T] class, that doesn't work play well with the Field
# annotations, unfortunately. Maybe someone smart will figure out how to make this idea
# work, but for now it's a wish, not something for a to-do list.


class PhysicalDimensions(CompatibleBaseModel):
    width: Annotated[float, Field(gt=0.0, lt=math.inf)]
    height: Annotated[float, Field(gt=0.0, lt=math.inf)]

    def __init__(self, width: float, height: float) -> None:
        super(PhysicalDimensions, self).__init__(width=width, height=height)


class SenselDimensions(CompatibleBaseModel):
    width: Annotated[int, Field(gt=0)]
    height: Annotated[float, Field(gt=0)]

    def __init__(self, w: int, h: int) -> None:
        super(SenselDimensions, self).__init__(width=w, height=h)


class ShutterAngle(PODModel):
    angle: Annotated[float, Field(gt=0.0, le=360.0)]

    def __init__(self, angle: float) -> None:
        super(ShutterAngle, self).__init__(angle=angle)

class StaticCamera(CompatibleBaseModel):
    capture_frame_rate: Optional[StrictlyPositiveRational] = None
    active_sensor_physical_dimensions: Optional[PhysicalDimensions] = None
    active_sensor_resolution: Optional[SenselDimensions] = None
    make: Optional[NonBlankUTF8String] = None
    model_name: Optional[NonBlankUTF8String] = None
    serial_number: Optional[NonBlankUTF8String] = None
    firmware_version: Optional[NonBlankUTF8String] = None
    label: Optional[NonBlankUTF8String] = None
    anamorphic_squeeze: Optional[StrictlyPositiveRational] = None
    isoSpeed: Optional[StrictlyPositiveInt] = None
    fdl_link: Optional[UUIDURN] = None
    shutter_angle: Optional[ShutterAngle] = None