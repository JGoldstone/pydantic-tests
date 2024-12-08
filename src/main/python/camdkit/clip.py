from typing import List, Optional

from pydantic import BaseModel

from camdkit.base_types import Rational, StrictlyPositiveRational, NonBlankUTF8String
from camdkit.model_types import SampleId, Synchronization, PhysicalDimensions, SenselDimensions


class Clip(BaseModel):
    # per clip
    active_sensor_physical_dimensions: Optional[PhysicalDimensions] = None
    active_sensor_resolution: Optional[SenselDimensions] = None
    anamorphic_squeeze: Optional[StrictlyPositiveRational] = None
    camera_make: Optional[NonBlankUTF8String] = None
    camera_model: Optional[NonBlankUTF8String] = None
    camera_firmware: Optional[NonBlankUTF8String] = None
    camera_serial_number: Optional[NonBlankUTF8String] = None
    camera_label: Optional[NonBlankUTF8String] = None
    capture_frame_rate: Optional[StrictlyPositiveRational] = None
    tracker_make: Optional[NonBlankUTF8String] = None
    tracker_model: Optional[NonBlankUTF8String] = None
    tracker_firmware: Optional[NonBlankUTF8String] = None
    tracker_serial_number: Optional[NonBlankUTF8String] = None
    entrance_pupil_offset: Optional[Rational] = None
    capture_fps: Optional[StrictlyPositiveRational] = None
    timing_frame_rate: Optional[StrictlyPositiveRational] = None
    related_sample_ids: Optional[List[SampleId]] = None
    timing_synchronization: Optional[Synchronization] = None
    # per-sample
    sample_id: Optional[SampleId] = None
