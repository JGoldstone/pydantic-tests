from typing import Optional

from pydantic import BaseModel

from camdkit.types import Rational, StrictlyPositiveRational, NonBlankUTF8String

class Clip(BaseModel):
    camera_make: Optional[NonBlankUTF8String]
    entrance_pupil_offset: Optional[Rational]
    capture_fps: Optional[StrictlyPositiveRational]


