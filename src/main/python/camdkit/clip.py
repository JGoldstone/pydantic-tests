#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for modeling clips"""

from typing import Annotated, Any

from pydantic import Field, field_validator

from camdkit.compatibility import CompatibleBaseModel
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
from camdkit.timing_types import Timing, TimingMode, Timestamp, Synchronization, Timecode
from camdkit.versioning_types import VersionedProtocol
from camdkit.transform_types import Transform


class Static(CompatibleBaseModel):
    duration: StrictlyPositiveRational | None = None
    camera: StaticCamera | None = None
    lens: StaticLens | None = None
    tracker: StaticTracker | None = None

    # noinspection PyNestedDecorators
    @field_validator("duration", mode="before")
    @classmethod
    def coerce_duration_to_strictly_positive_rational(cls, v):
        return rationalize_strictly_and_positively(v)

class Clip(CompatibleBaseModel):
    static: Static | None = None

    tracker: Tracker | None = None
    timing: Timing | None = None
    lens: Lens | None = None

    # The "global_" prefix is here because, without it, we would have BaseModel attributes
    # with the same name, from the user's POV, as the property
    global_protocol: Annotated[tuple[VersionedProtocol, ...] | None, Field(alias="protocol")] = None
    global_sample_id: Annotated[tuple[UUIDURN, ...] | None, Field(alias="sampleId")] = None
    global_source_id: Annotated[tuple[UUIDURN, ...] | None, Field(alias="sourceId")] = None
    global_source_number: Annotated[tuple[NonNegativeInt, ...] | None, Field(alias="sourceNumber")] = None
    global_related_sample_ids: Annotated[tuple[tuple[UUIDURN, ...], ...] | None, Field(alias="relatedSampleIds")] = None
    global_global_stage: Annotated[tuple[GlobalPosition, ...] | None, Field(alias="globalStage")] = None
    global_transforms: Annotated[tuple[tuple[Transform, ...], ...] | None, Field(alias="transforms")] = None

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

    # TODO: introspect all of these, or at least the static ones

    @property
    def duration(self) -> StrictlyPositiveRational | None:
        return self.value_from_hierarchy(('static', 'duration'))

    @duration.setter
    def duration(self, value: StrictlyPositiveRational | None) -> None:
        self.set_through_hierarchy((
            ('static', Static),),
            'duration', value)

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
