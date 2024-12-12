#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling clips"""

from typing import Optional, Any

from pydantic import Field

from camdkit.backwards import CompatibleBaseModel
from camdkit.numeric_types import NonNegativeInt, StrictlyPositiveRational
from camdkit.lens_types import StaticLens, Lens
from camdkit.camera_types import StaticCamera, PhysicalDimensions, SenselDimensions
from camdkit.string_types import NonBlankUTF8String, UUIDURN
from camdkit.tracker_types import StaticTracker, Tracker
from camdkit.timing_types import Timing
from camdkit.transform_types import Transforms


class GlobalPosition(CompatibleBaseModel):
    """Global ENU and geodetic coördinates
    Reference:. https://en.wikipedia.org/wiki/Local_tangent_plane_coordinates
    """
    E: float  # East (meters)
    N: float  # North (meters)
    U: float  # Up (meters)
    lat0: float = Field(..., ge=-90, le=90)  # latitude (degrees)
    long0: float = Field(..., ge=-180, le=180)  # longitude (degrees)
    h0: float  # height (meters)

    def __init__(self, e: float, n: float, u: float, lat0: float, long0: float, h0: float):
        super(GlobalPosition, self).__init__(E=e, N=n, U=u, lat0=lat0, long0=long0, h0=h0)


class Static(CompatibleBaseModel):
    duration: Optional[StrictlyPositiveRational] = None
    camera: Optional[StaticCamera] = None
    lens: Optional[StaticLens] = None
    tracker: Optional[StaticTracker] = None


class Clip(CompatibleBaseModel):
    static: Optional[Static] = None
    sample_id: Optional[tuple[UUIDURN]] = None
    source_id: Optional[tuple[UUIDURN]] = None
    source_number: Optional[tuple[NonNegativeInt]] = None
    related_sample_ids: Optional[tuple[tuple[UUIDURN]]] = None
    global_stage: Optional[tuple[GlobalPosition]] = None
    tracker: Optional[Tracker] = None
    timing: Optional[Timing] = None
    transforms: Optional[tuple[Transforms]] = None
    lens: Optional[Lens] = None

    def value_from_hierarchy(self, attrs: tuple[str, ...]):
        obj = self
        for attr in attrs:
            try:
                obj = getattr(obj, attr)
            except AttributeError:
                return None
        return obj

    def set_through_hierarchy(self, attrs_and_classes: tuple[tuple[str, type], ...],
                              name: str, value: Any) -> None:
        obj = self
        for (attr, attr_type) in attrs_and_classes:
            if not hasattr(obj, attr) or getattr(obj, attr) is None:
                setattr(obj, attr, attr_type())
            obj = getattr(obj, attr)
        setattr(obj, name, value)

    # TODO: introspect all of these, or at least the static ones

    @property
    def capture_frame_rate(self) -> StrictlyPositiveRational:
        return self.value_from_hierarchy(('static', 'camera', 'capture_frame_rate'))

    @capture_frame_rate.setter
    def capture_frame_rate(self, value: StrictlyPositiveRational) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'capture_frame_rate',
                                   value)

    @property
    def active_sensor_physical_dimensions(self) -> PhysicalDimensions:
        return self.value_from_hierarchy(('static', 'camera', 'active_sensor_physical_dimensions'))

    @active_sensor_physical_dimensions.setter
    def active_sensor_physical_dimensions(self, value: PhysicalDimensions) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'active_sensor_physical_dimensions',
                                   value)

    @property
    def active_sensor_resolution(self) -> SenselDimensions:
        return self.value_from_hierarchy(('static', 'camera', 'active_sensor_resolution'))

    @active_sensor_resolution.setter
    def active_sensor_resolution(self, value: SenselDimensions) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'active_sensor_resolution',
                                   value)

    @property
    def anamorphic_squeeze(self) -> StrictlyPositiveRational:
        return self.value_from_hierarchy(('static', 'camera', 'anamorphic_squeeze'))

    @anamorphic_squeeze.setter
    def anamorphic_squeeze(self, value: StrictlyPositiveRational) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'anamorphic_squeeze',
                                   value)

    @property
    def camera_make(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'make'))

    @camera_make.setter
    def camera_make(self, value: NonBlankUTF8String) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'make',
                                   value)

    @property
    def camera_model(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'model_name'))

    @camera_model.setter
    def camera_model(self, value: NonBlankUTF8String) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'model_name',
                                   value)

    @property
    def camera_serial_number(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'serial_number'))

    @camera_serial_number.setter
    def camera_serial_number(self, value: NonBlankUTF8String) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'serial_number',
                                   value)

    @property
    def camera_firmware(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'firmware_version'))

    @camera_firmware.setter
    def camera_firmware(self, value: NonBlankUTF8String) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'firmware_version',
                                   value)

    @property
    def camera_label(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'label'))

    @camera_label.setter
    def camera_label(self, value: NonBlankUTF8String) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'label',
                                   value)

    @property
    def iso(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'iso'))

    @iso.setter
    def iso(self, value: NonBlankUTF8String) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'iso',
                                   value)

    @property
    def fdl_link(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'fdl_link'))

    @fdl_link.setter
    def fdl_link(self, value: NonBlankUTF8String) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'fdl_link',
                                   value)

    @property
    def shutter_angle(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'shutter_angle'))

    @shutter_angle.setter
    def shutter_angle(self, value: NonBlankUTF8String) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'shutter_angle',
                                   value)


    @property
    def duration(self) -> StrictlyPositiveRational:
        return self.static.duration

    @duration.setter
    def duration(self, value) -> None:
        self.static.duration = value
