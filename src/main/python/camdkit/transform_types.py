from typing import Optional

from pydantic import Field

from camdkit.backwards import CompatibleBaseModel
from camdkit.model_types import UUIDURN


class Vector3(CompatibleBaseModel):
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        super(Vector3, self).__init__(x=x, y=y, z=z)


class Rotator3(CompatibleBaseModel):
    x: float = Field(..., ge=0.0, le=360.0)  # pan
    y: float = Field(..., ge=-90.0, le=90.0)  # tilt
    z: float = Field(..., ge=0.0, le=360.0)

    def __init__(self, x: float, y: float, z: float):
        super(Rotator3, self).__init__(x=x, y=y, z=z)


class Transforms(CompatibleBaseModel):
    translation: Vector3
    rotation: Rotator3
    scale: Optional[Vector3] = None
    id: Optional[UUIDURN] = None
    parent_id: Optional[UUIDURN] = None
