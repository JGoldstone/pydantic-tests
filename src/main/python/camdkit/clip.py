from typing import List, Optional, Any, Self

from pydantic import BaseModel

from camdkit.base_types import Sampling, Rational, StrictlyPositiveRational, NonBlankUTF8String, SampleId, FrameRate


class Clip(BaseModel):
    sample_id: SampleId
    camera_make: Optional[NonBlankUTF8String] = None
    entrance_pupil_offset: Optional[Rational] = None
    capture_fps: Optional[FrameRate] = None
    timing_frame_rate: Optional[FrameRate] = None
    related_sample_ids: Optional[List[SampleId]] = None

    def __init__(self, s: SampleId, **kwargs):
        super(Clip, self).__init__(sample_id=s, **kwargs)
