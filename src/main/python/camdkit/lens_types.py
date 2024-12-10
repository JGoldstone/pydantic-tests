from typing import Optional

from camdkit.backwards import CompatibleBaseModel
from camdkit.base_types import (NonBlankUTF8String,
                                NonNegativeFloat, StrictlyPositiveFloat,
                                NonNegativeInt)


class StaticLens(CompatibleBaseModel):
    distortion_overscan_max: Optional[float] = None
    undistortion_overscan_max: Optional[float] = None
    make: Optional[NonBlankUTF8String] = None
    model_name: Optional[NonBlankUTF8String] = None
    serial_number: Optional[NonBlankUTF8String] = None
    firmware_version: Optional[NonBlankUTF8String] = None
    nominal_focal_length: Optional[StrictlyPositiveFloat] = None


class Distortion(CompatibleBaseModel):
    radial: tuple[float, ...]
    tangential: Optional[tuple[float, ...]] = None
    model: Optional[str] = None

    def __init__(self, r: tuple[float, ...],
                 t: Optional[tuple[float, ...]] = None,
                 m: Optional[str] = None):
        super(Distortion, self).__init__(radial=r, tangential=t, model=m)


class PlanarOffset(CompatibleBaseModel):
    x: float
    y: float


class FizEncoder[T](CompatibleBaseModel):
    focus: T
    iris: T
    zoom: T


class ExposureFalloff(CompatibleBaseModel):
    a1: float
    a2: Optional[float] = None
    a3: Optional[float] = None


class Lens(CompatibleBaseModel):
    custom: Optional[tuple[tuple]] = None  # WTF?
    distortion: Optional[tuple[Distortion]] = None
    distortion_overscan: Optional[tuple[tuple[float]]] = None  # How many, exactly?
    undistortion_overscan: Optional[tuple[tuple[float]]] = None  # Again, how many?
    distortion_offset: Optional[tuple[tuple[PlanarOffset]]] = None
    encoders: Optional[tuple[tuple[FizEncoder[NonNegativeFloat]]]] = None
    entrance_pupil_offset: Optional[tuple[float]] = None
    exposure_falloff: Optional[tuple[ExposureFalloff]] = None
    f_number: Optional[tuple[StrictlyPositiveFloat]] = None
    focal_length: Optional[tuple[StrictlyPositiveFloat]] = None
    focus_distance: Optional[tuple[StrictlyPositiveFloat]] = None
    projection_offset: Optional[tuple[PlanarOffset]] = None
    raw_encoders: Optional[tuple[FizEncoder[NonNegativeInt]]] = None
    t_number: Optional[tuple[StrictlyPositiveFloat]] = None
    undistortion: Optional[tuple[Distortion]] = None
