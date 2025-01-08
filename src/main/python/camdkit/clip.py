#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling clips"""
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic.json_schema import JsonSchemaMode, JsonSchemaValue

from camdkit.compatibility import (CompatibleBaseModel,
                                   UUID_URN,
                                   NON_NEGATIVE_INTEGER,
                                   STRICTLY_POSITIVE_RATIONAL,
                                   PROTOCOL,
                                   ARRAY,
                                   GLOBAL_POSITION,
                                   TRANSFORMS)
from camdkit.units import METER, METERS_AND_DEGREES, SECOND
from camdkit.numeric_types import (NonNegativeInt,
                                   UnityOrGreaterFloat,
                                   StrictlyPositiveRational,
                                   rationalize_strictly_and_positively)
from camdkit.lens_types import (StaticLens, Lens,
                                Distortion, DistortionOffset, ProjectionOffset,
                                FizEncoders, RawFizEncoders)
from camdkit.camera_types import StaticCamera, PhysicalDimensions, SenselDimensions
from camdkit.string_types import NonBlankUTF8String, UUIDURN
from camdkit.tracker_types import StaticTracker, Tracker, GlobalPosition
from camdkit.timing_types import Timing, TimingMode, Timestamp, Synchronization, Timecode, Sampling
from camdkit.versioning_types import VersionedProtocol
from camdkit.transform_types import Transform

__all__ = ['Clip']

CLIP_SCHEMA_PRELUDE = {
    "$id": "https://opentrackio.org/schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema"
}


# TODO: introspect all of these, or at least the static ones
class Static(CompatibleBaseModel):
    duration: Annotated[StrictlyPositiveRational | None,
      Field(json_schema_extra={"clip_property": "duration",
                               "constraints": STRICTLY_POSITIVE_RATIONAL,
                               "units": SECOND})] = None
    """Duration of the clip"""

    camera: StaticCamera = StaticCamera()
    lens: StaticLens = StaticLens()
    tracker: StaticTracker = StaticTracker()

    # noinspection PyNestedDecorators
    @field_validator("duration", mode="before")
    @classmethod
    def coerce_duration_to_strictly_positive_rational(cls, v):
        return rationalize_strictly_and_positively(v)

class Clip(CompatibleBaseModel):
    static: Static = Static()

    tracker: Tracker = Tracker()
    timing: Timing = Timing()
    lens: Lens = Lens()

    # The "global_" prefix is here because, without it, we would have BaseModel attributes
    # with the same name, from the user's POV, as the property
    global_protocol: Annotated[tuple[VersionedProtocol, ...] | None,
      Field(alias="protocol",
            json_schema_extra={"clip_property": "protocol",
                               "constraints": PROTOCOL})] = None
    """Name of the protocol in which the sample is being employed, and
    version of that protocol
    """

    global_sample_id: Annotated[tuple[UUIDURN, ...] | None,
      Field(alias="sampleId",
            json_schema_extra={"clip_property": "sample_id",
                               "constraints": UUID_URN})] = None
    """URN serving as unique identifier of the sample in which data is
    being transported.
    """

    global_source_id: Annotated[tuple[UUIDURN, ...] | None,
      Field(alias="sourceId",
            json_schema_extra={"clip_property": "source_id",
                               "constraints": UUID_URN})] = None
    """URN serving as unique identifier of the source from which data is
    being transported.
    """

    global_source_number: Annotated[tuple[NonNegativeInt, ...] | None,
      Field(alias="sourceNumber",
            json_schema_extra={"clip_property": "source_number",
                               "constraints": NON_NEGATIVE_INTEGER})] = None
    """Number that identifies the index of the stream from a source from which
    data is being transported. This is most important in the case where a source
    is producing multiple streams of samples.
    """

    global_related_sample_ids: Annotated[tuple[tuple[UUIDURN, ...], ...] | None,
      Field(alias="relatedSampleIds",
            json_schema_extra={"clip_property": "related_sample_ids",
                               "constraints": ARRAY})] = None
    """List of sampleId properties of samples related to this sample. The
    existence of a sample with a given sampleId is not guaranteed.
    """

    global_global_stage: Annotated[tuple[GlobalPosition, ...] | None,
      Field(alias="globalStage",
            json_schema_extra={"units": METER,
                               "clip_property": "global_stage",
                               "constraints": GLOBAL_POSITION})] = None
    """Position of stage origin in global ENU and geodetic coordinates
    (E, N, U, lat0, lon0, h0). Note this may be dynamic if the stage is
    inside a moving vehicle.
    """

    global_transforms: Annotated[tuple[tuple[Transform, ...], ...] | None,
      Field(alias="transforms",
            min_length=1,
            json_schema_extra={"units": METERS_AND_DEGREES,
                               "clip_property": "transforms",
                               "constraints": TRANSFORMS,
                               "uniqueItems": False})] = None
    """A list of transforms.
    Transforms are composed in order with the last in the list representing
    the X,Y,Z in meters of camera sensor relative to stage origin.
    The Z axis points upwards and the coordinate system is right-handed.
    Y points in the forward camera direction (when pan, tilt and roll are
    zero).
    For example in an LED volume Y would point towards the centre of the
    LED wall and so X would point to camera-right.
    Rotation expressed as euler angles in degrees of the camera sensor
    relative to stage origin
    Rotations are intrinsic and are measured around the axes ZXY, commonly
    referred to as [pan, tilt, roll]
    Notes on Euler angles:
    Euler angles are human readable and unlike quarternions, provide the
    ability for cycles (with angles >360 or <0 degrees).
    Where a tracking system is providing the pose of a virtual camera,
    gimbal lock does not present the physical challenges of a robotic
    system.
    Conversion to and from quarternions is trivial with an acceptable loss
    of precision.
    """

    @classmethod
    def traverse_json_schema(cls,
                             name: str,
                             level: JsonSchemaValue,
                             parents: list[str],
                             function: Callable[[str, JsonSchemaValue, list[str]], None]) -> None:
        if level.get("properties", None):
            for key, value in level["properties"].items():
                if "clip_property" in value:
                    function(key, value, parents + [name])
                elif "properties" in value:
                    Clip.traverse_json_schema(key, value, parents + [name], function)

    @classmethod
    def make_documentation(cls) -> list[dict[str, str]]:
        full_schema = Clip.make_json_schema(mode='validation',
                                            exclude_camdkit_internals=False)
        documentation: list[dict[str, str]] = []

        def document_clip_property(key: str,
                                   property_schema: JsonSchemaValue,
                                   parents: list[str]) -> None:
            if parents and parents[0] == '':
                parents.pop(0)
            # print(f"documenting clip property: {property_schema["clip_property"]}; parents {parents}")
            documentation.append({
                "python_name": property_schema["clip_property"],
                "canonical_name": key,
                "description": property_schema["description"],
                "constraints": property_schema["constraints"] if "constraints" in property_schema else None,
                "sampling": (Sampling.STATIC.value.capitalize()
                             if "static" in parents or property_schema["clip_property"] == "duration"
                             else Sampling.REGULAR.value.capitalize()),
                "section": (parents[-1]
                            if parents and property_schema["clip_property"] != "duration"
                            else "None"),
                "units": property_schema["units"] if "units" in property_schema else "None"
            })

        Clip.traverse_json_schema("", full_schema, [], document_clip_property)
        return documentation

    @classmethod
    def make_json_schema(cls, mode: JsonSchemaMode = 'serialization',
                         exclude_camdkit_internals: bool = True) -> JsonSchemaValue:
        result = CLIP_SCHEMA_PRELUDE | super(Clip, cls).make_json_schema(mode, exclude_camdkit_internals)
        return result

    def value_from_hierarchy(self, attrs: tuple[str, ...]):
        obj = self
        for attr in attrs:
            try:
                obj = getattr(obj, attr)
            except AttributeError:
                return None
        return obj

    def set_through_hierarchy(self, attrs_and_classes: tuple[tuple[str, type], ...] | None,
                              name: str, value: Any) -> None:
        obj = self
        if attrs_and_classes:
            for (attr, attr_type) in attrs_and_classes:
                if not hasattr(obj, attr) or getattr(obj, attr) is None:
                    setattr(obj, attr, attr_type())
                obj = getattr(obj, attr)
        setattr(obj, name, value)

    # @property
    # def duration(self) -> StrictlyPositiveRational | None:
    #     return self.value_from_hierarchy(('static', 'duration'))
    #
    # @duration.setter
    # def duration(self, value: StrictlyPositiveRational | None) -> None:
    #     self.set_through_hierarchy((
    #         ('static', Static),),
    #         'duration', value)

    @classmethod
    def add_property(cls, name: str, model_path: tuple[tuple[str, type], ...]):

        def get_through_path(self):
            obj = self
            model_fields: list[str] = [mf for mf, mc in model_path]
            model_fields.append(name)
            for model_field in model_fields:
                try:
                    obj = getattr(obj, model_field)
                except AttributeError:
                    return None
            return obj

        def set_through_path(self, value: Any) -> None:
            obj = self
            if model_path:
                for model_field, model_class in model_path:
                    if not hasattr(obj, model_field) or getattr(obj, model_field) is None:
                        setattr(obj, model_field, model_class())
                    obj = getattr(obj, model_field)
            setattr(obj, name, value)

        print(f"about to add property {name} to class {cls}")
        setattr(cls, name, property(get_through_path, set_through_path))
        print("done with adding property {name} to class {cls}")

    @property
    def capture_frame_rate(self) -> StrictlyPositiveRational:
        return self.value_from_hierarchy(('static', 'camera', 'capture_frame_rate'))

    @capture_frame_rate.setter
    def capture_frame_rate(self, value: StrictlyPositiveRational | None) -> None:
        self.set_through_hierarchy((
            ('static', Static),
            ('camera', StaticCamera)),
            'capture_frame_rate', value)

    @property
    def active_sensor_physical_dimensions(self) -> PhysicalDimensions:
        return self.value_from_hierarchy(('static', 'camera', 'active_sensor_physical_dimensions'))

    @active_sensor_physical_dimensions.setter
    def active_sensor_physical_dimensions(self, value: PhysicalDimensions | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'active_sensor_physical_dimensions',
                                   value)

    @property
    def active_sensor_resolution(self) -> SenselDimensions:
        return self.value_from_hierarchy(('static', 'camera', 'active_sensor_resolution'))

    @active_sensor_resolution.setter
    def active_sensor_resolution(self, value: SenselDimensions  | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'active_sensor_resolution',
                                   value)

    @property
    def anamorphic_squeeze(self) -> StrictlyPositiveRational:
        return self.value_from_hierarchy(('static', 'camera', 'anamorphic_squeeze'))

    @anamorphic_squeeze.setter
    def anamorphic_squeeze(self, value: StrictlyPositiveRational | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'anamorphic_squeeze',
                                   value)

    @property
    def camera_make(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'make'))

    @camera_make.setter
    def camera_make(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'make',
                                   value)

    @property
    def camera_model(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'model'))

    @camera_model.setter
    def camera_model(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'model',
                                   value)

    @property
    def camera_serial_number(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'serial_number'))

    @camera_serial_number.setter
    def camera_serial_number(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'serial_number',
                                   value)

    @property
    def camera_firmware(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'firmware_version'))

    @camera_firmware.setter
    def camera_firmware(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'firmware_version',
                                   value)

    @property
    def camera_label(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'label'))

    @camera_label.setter
    def camera_label(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'label',
                                   value)

    @property
    def iso(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'iso'))

    @iso.setter
    def iso(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'iso',
                                   value)

    @property
    def fdl_link(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'fdl_link'))

    @fdl_link.setter
    def fdl_link(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'fdl_link',
                                   value)

    @property
    def shutter_angle(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'camera', 'shutter_angle'))

    @shutter_angle.setter
    def shutter_angle(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('camera', StaticCamera)),
                                   'shutter_angle',
                                   value)
    
    @property
    def lens_distortion_overscan_max(self) -> UnityOrGreaterFloat:
        return self.value_from_hierarchy(('static', 'lens', 'distortion_overscan_max'))
    
    @lens_distortion_overscan_max.setter
    def lens_distortion_overscan_max(self, value: UnityOrGreaterFloat | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('lens', StaticLens)),
                                   'distortion_overscan_max',
                                   value)
    
    @property
    def lens_undistortion_overscan_max(self) -> UnityOrGreaterFloat:
        return self.value_from_hierarchy(('static', 'lens', 'undistortion_overscan_max'))
    
    @lens_undistortion_overscan_max.setter
    def lens_undistortion_overscan_max(self, value: UnityOrGreaterFloat | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('lens', StaticLens)),
                                   'undistortion_overscan_max',
                                   value)

    @property
    def lens_distortion_is_projection(self) -> bool:
        return self.value_from_hierarchy(('static', 'lens', 'distortion_is_projection'))

    @lens_distortion_is_projection.setter
    def lens_distortion_is_projection(self, value: bool) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('lens', StaticLens)),
                                   'distortion_is_projection',
                                   value)

    @property
    def lens_make(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'lens', 'make'))

    @lens_make.setter
    def lens_make(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('lens', StaticLens)),
                                   'make',
                                   value)

    @property
    def lens_model(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'lens', 'model'))

    @lens_model.setter
    def lens_model(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('lens', StaticLens)),
                                   'model',
                                   value)

    @property
    def lens_serial_number(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'lens', 'serial_number'))

    @lens_serial_number.setter
    def lens_serial_number(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('lens', StaticLens)),
                                   'serial_number',
                                   value)

    @property
    def lens_firmware(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'lens', 'firmware_version'))

    @lens_firmware.setter
    def lens_firmware(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('lens', StaticLens)),
                                   'firmware_version',
                                   value)

    @property
    def lens_nominal_focal_length(self) -> NonBlankUTF8String | None:
        return self.value_from_hierarchy(('static', 'lens', 'nominal_focal_length'))

    @lens_nominal_focal_length.setter
    def lens_nominal_focal_length(self, value: NonBlankUTF8String | None) -> None:
        self.set_through_hierarchy((('static', Static),
                                    ('lens', StaticLens)),
                                   'nominal_focal_length',
                                   value)

    @property
    def lens_custom(self) -> tuple[tuple[Any, ...], ...] | None:
        return self.value_from_hierarchy(('lens', 'custom'))

    @lens_custom.setter
    def lens_custom(self, value: tuple[tuple[Any, ...], ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'custom',
                                   value)

    @property
    def lens_distortions(self) -> tuple[tuple[Distortion, ...], ...] | None:
        return self.value_from_hierarchy(('lens', 'distortion'))

    @lens_distortions.setter
    def lens_distortions(self, value: tuple[tuple[Distortion, ...], ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'distortion',
                                   value)

    @property
    def lens_distortion_overscan(self) -> tuple[float, ...] | None:
        return self.value_from_hierarchy(('lens', 'distortion_overscan'))

    @lens_distortion_overscan.setter
    def lens_distortion_overscan(self, value: tuple[float, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'distortion_overscan',
                                   value)

    @property
    def lens_undistortion_overscan(self) -> tuple[float, ...] | None:
        return self.value_from_hierarchy(('lens', 'undistortion_overscan'))

    @lens_undistortion_overscan.setter
    def lens_undistortion_overscan(self, value: tuple[float, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'undistortion_overscan',
                                   value)

    @property
    def lens_distortion_offset(self) -> tuple[DistortionOffset, ...] | None:
        return self.value_from_hierarchy(('lens', 'distortion_offset'))

    @lens_distortion_offset.setter
    def lens_distortion_offset(self, value: tuple[DistortionOffset, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'distortion_offset',
                                   value)

    @property
    def lens_encoders(self) -> tuple[FizEncoders, ...] | None:
        return self.value_from_hierarchy(('lens', 'encoders'))

    @lens_encoders.setter
    def lens_encoders(self, value: tuple[FizEncoders, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'encoders',
                                   value)

    @property
    def lens_entrance_pupil_offset(self) -> tuple[float, ...] | None:
        return self.value_from_hierarchy(('lens', 'entrance_pupil_offset'))

    @lens_entrance_pupil_offset.setter
    def lens_entrance_pupil_offset(self, value: tuple[float, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'entrance_pupil_offset',
                                   value)

    @property
    def lens_exposure_falloff(self) -> tuple[float, ...] | None:
        return self.value_from_hierarchy(('lens', 'exposure_falloff'))

    @lens_exposure_falloff.setter
    def lens_exposure_falloff(self, value: tuple[float, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'exposure_falloff',
                                   value)

    @property
    def lens_f_number(self) -> tuple[float, ...] | None:
        return self.value_from_hierarchy(('lens', 'f_number'))

    @lens_f_number.setter
    def lens_f_number(self, value: tuple[float, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'f_number',
                                   value)

    @property
    def lens_focal_length(self) -> tuple[float, ...] | None:
        return self.value_from_hierarchy(('lens', 'focal_length'))

    @lens_focal_length.setter
    def lens_focal_length(self, value: tuple[float, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'focal_length',
                                   value)

    @property
    def lens_focus_distance(self) -> tuple[float, ...] | None:
        return self.value_from_hierarchy(('lens', 'focus_distance'))

    @lens_focus_distance.setter
    def lens_focus_distance(self, value: tuple[float, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'focus_distance',
                                   value)

    @property
    def lens_projection_offset(self) -> tuple[ProjectionOffset, ...] | None:
        return self.value_from_hierarchy(('lens', 'projection_offset'))

    @lens_projection_offset.setter
    def lens_projection_offset(self, value: tuple[ProjectionOffset, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'projection_offset',
                                   value)

    @property
    def lens_raw_encoders(self) -> tuple[RawFizEncoders, ...] | None:
        return self.value_from_hierarchy(('lens', 'raw_encoders'))

    @lens_raw_encoders.setter
    def lens_raw_encoders(self, value: tuple[RawFizEncoders, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'raw_encoders',
                                   value)

    @property
    def lens_t_number(self) -> tuple[float, ...] | None:
        return self.value_from_hierarchy(('lens', 't_number'))

    @lens_t_number.setter
    def lens_t_number(self, value: tuple[float, ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   't_number',
                                   value)

    @property
    def lens_undistortions(self) -> tuple[tuple[Distortion, ...], ...] | None:
        return self.value_from_hierarchy(('lens', 'undistortion'))

    @lens_undistortions.setter
    def lens_undistortions(self, value: tuple[tuple[Distortion, ...], ...] | None) -> None:
        self.set_through_hierarchy((('lens', Lens),),
                                   'undistortion',
                                   value)

    @property
    def timing_mode(self) -> tuple[TimingMode, ...] | None:
        return self.value_from_hierarchy(('timing', 'mode'))
    
    @timing_mode.setter
    def timing_mode(self, value: tuple[TimingMode, ...] | None) -> None:
        self.set_through_hierarchy((('timing', Timing),),
                                   'mode',
                                   value)

    @property
    def timing_recorded_timestamp(self) -> tuple[Timestamp, ...] | None:
        return self.value_from_hierarchy(('timing', 'recorded_timestamp'))
    
    @timing_recorded_timestamp.setter
    def timing_recorded_timestamp(self, value: tuple[Timestamp, ...] | None) -> None:
        self.set_through_hierarchy((('timing', Timing),),
                                   'recorded_timestamp',
                                   value)

    @property
    def timing_sample_rate(self) -> tuple[StrictlyPositiveRational, ...] | None:
        return self.value_from_hierarchy(('timing', 'sample_rate'))
    
    @timing_sample_rate.setter
    def timing_sample_rate(self, value: tuple[StrictlyPositiveRational, ...] | None) -> None:
        self.set_through_hierarchy((('timing', Timing),),
                                   'sample_rate',
                                   value)

    @property
    def timing_sample_timestamp(self) -> tuple[Timestamp, ...] | None:
        return self.value_from_hierarchy(('timing', 'sample_timestamp'))
    
    @timing_sample_timestamp.setter
    def timing_sample_timestamp(self, value: tuple[Timestamp, ...] | None) -> None:
        self.set_through_hierarchy((('timing', Timing),),
                                   'sample_timestamp',
                                   value)

    @property
    def timing_sequence_number(self) -> tuple[NonNegativeInt, ...] | None:
        return self.value_from_hierarchy(('timing', 'sequence_number'))
    
    @timing_sequence_number.setter
    def timing_sequence_number(self, value: tuple[NonNegativeInt, ...] | None) -> None:
        self.set_through_hierarchy((('timing', Timing),),
                                   'sequence_number',
                                   value)

    @property
    def timing_synchronization(self) -> tuple[Synchronization, ...] | None:
        return self.value_from_hierarchy(('timing', 'synchronization'))
    
    @timing_synchronization.setter
    def timing_synchronization(self, value: tuple[Synchronization, ...] | None) -> None:
        self.set_through_hierarchy((('timing', Timing),),
                                   'synchronization',
                                   value)

    @property
    def timing_timecode(self) -> tuple[Timecode, ...] | None:
        return self.value_from_hierarchy(('timing', 'timecode'))
    
    @timing_timecode.setter
    def timing_timecode(self, value: tuple[Timecode, ...] | None) -> None:
        self.set_through_hierarchy((('timing', Timing),),
                                   'timecode',
                                   value)

    @property
    def tracker_make(self) -> tuple[NonBlankUTF8String, ...] | None:
        return self.value_from_hierarchy(('static', 'tracker', 'make'))

    @tracker_make.setter
    def tracker_make(self, value: tuple[NonBlankUTF8String, ...] | None) -> None:
        self.set_through_hierarchy((
            ('static', Static),
            ('tracker', StaticTracker)),
            'make',
            value)

    @property
    def tracker_model(self) -> tuple[NonBlankUTF8String, ...] | None:
        return self.value_from_hierarchy(('static', 'tracker', 'model'))

    @tracker_model.setter
    def tracker_model(self, value: tuple[NonBlankUTF8String, ...] | None) -> None:
        self.set_through_hierarchy((
            ('static', Static),
            ('tracker', StaticTracker)),
            'model', value)

    @property
    def tracker_firmware(self) -> tuple[NonBlankUTF8String, ...] | None:
        return self.value_from_hierarchy(('static', 'tracker', 'firmware'))

    @tracker_firmware.setter
    def tracker_firmware(self, value: tuple[NonBlankUTF8String, ...] | None) -> None:
        self.set_through_hierarchy((
            ('static', Static),
            ('tracker', StaticTracker)),
            'firmware', value)

    @property
    def tracker_serial_number(self) -> tuple[NonBlankUTF8String, ...] | None:
        return self.value_from_hierarchy(('static', 'tracker', 'serial_number'))

    @tracker_serial_number.setter
    def tracker_serial_number(self, value: tuple[NonBlankUTF8String, ...] | None) -> None:
        self.set_through_hierarchy((
            ('static', Static),
            ('tracker', StaticTracker)),
            'serial_number', value)

    @property
    def tracker_status(self) -> tuple[NonBlankUTF8String, ...] | None:
        return self.value_from_hierarchy(('tracker', 'status'))
    
    @tracker_status.setter
    def tracker_status(self, value: tuple[NonBlankUTF8String, ...] | None) -> None:
        self.set_through_hierarchy((
            ('tracker', Tracker),),
            'status', value)

    @property
    def tracker_recording(self) -> tuple[bool, ...] | None:
        return self.value_from_hierarchy(('tracker', 'recording'))
    
    @tracker_recording.setter
    def tracker_recording(self, value: tuple[bool, ...] | None) -> None:
        self.set_through_hierarchy((
            ('tracker', Tracker),),
            'recording', value)

    @property
    def tracker_slate(self) -> tuple[NonBlankUTF8String, ...] | None:
        return self.value_from_hierarchy(('tracker', 'slate'))

    @tracker_slate.setter
    def tracker_slate(self, value: tuple[NonBlankUTF8String, ...] | None) -> None:
        self.set_through_hierarchy((
            ('tracker', Tracker),),
            'slate', value)

    @property
    def tracker_notes(self) -> tuple[NonBlankUTF8String, ...] | None:
        return self.value_from_hierarchy(('tracker', 'notes'))

    @tracker_notes.setter
    def tracker_notes(self, value: tuple[NonBlankUTF8String, ...] | None) -> None:
        self.set_through_hierarchy((
            ('tracker', Tracker),),
            'notes', value)

    @property
    def protocol(self) -> tuple[VersionedProtocol, ...] | None:
        return self.value_from_hierarchy(('global_protocol',))

    @protocol.setter
    def protocol(self, value):
        self.set_through_hierarchy(
            None,
            'global_protocol', value)

    @property
    def sample_id(self) -> tuple[UUIDURN, ...] | None:
        return self.value_from_hierarchy(('global_sample_id',))

    @sample_id.setter
    def sample_id(self, value: tuple[UUIDURN, ...] | None) -> None:
        self.set_through_hierarchy(
            None,
            'global_sample_id', value)

    @property
    def source_id(self) -> tuple[UUIDURN, ...] | None:
        return self.value_from_hierarchy(('global_source_id',))

    @source_id.setter
    def source_id(self, value: tuple[UUIDURN, ...] | None) -> None:
        self.set_through_hierarchy(
            None,
            'global_source_id', value)

    @property
    def source_number(self) -> tuple[NonNegativeInt, ...] | None:
        return self.value_from_hierarchy(('global_source_number',))

    @source_number.setter
    def source_number(self, value: tuple[NonNegativeInt, ...] | None) -> None:
        self.set_through_hierarchy(
            None,
            'global_source_number', value)

    @property
    def related_sample_ids(self) -> tuple[tuple[UUIDURN, ...], ...] | None:
        return self.value_from_hierarchy(('global_related_sample_ids',))

    @related_sample_ids.setter
    def related_sample_ids(self, value: tuple[tuple[UUIDURN, ...], ...] | None) -> None:
        self.set_through_hierarchy(
            None,
            'global_related_sample_ids', value)

    @property
    def global_stage(self) -> tuple[tuple[GlobalPosition, ...], ...] | None:
        return self.value_from_hierarchy(('global_global_stage',))

    @global_stage.setter
    def global_stage(self, value: tuple[tuple[GlobalPosition, ...], ...] | None) -> None:
        self.set_through_hierarchy(
            None,
            'global_global_stage', value)

    @property
    def transforms(self) -> tuple[tuple[Transform, ...], ...] | None:
        return self.value_from_hierarchy(('global_transforms',))

    @transforms.setter
    def transforms(self, value: tuple[tuple[Transform, ...], ...] | None) -> None:
        self.set_through_hierarchy(
            None,
            'global_transforms', value)
