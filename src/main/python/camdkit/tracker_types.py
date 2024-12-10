from typing import Optional

from camdkit.base_types import NonBlankUTF8String
from camdkit.backwards import CompatibleBaseModel


class StaticTracker(CompatibleBaseModel):
    make: Optional[NonBlankUTF8String] = None
    model_name: Optional[NonBlankUTF8String] = None
    serial_number: Optional[NonBlankUTF8String] = None
    firmware_version: Optional[NonBlankUTF8String] = None


class Tracker(CompatibleBaseModel):
    notes: Optional[tuple[NonBlankUTF8String]] = None
    recording: Optional[tuple[bool]] = None
    slate: Optional[tuple[NonBlankUTF8String]] = None
    status: Optional[tuple[NonBlankUTF8String]] = None
