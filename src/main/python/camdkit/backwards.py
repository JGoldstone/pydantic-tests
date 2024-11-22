
from typing import Optional

from pydantic import BaseModel, ValidationError

# For compatibility with existing code
class CamdkitParameter(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def validate(value) -> bool:
        # I feel icky. This will fail the moment someone makes a
        # parameter with more than one superclass.
        subclasses = __class__.__subclasses__()
        assert len(subclasses) == 1
        subclass = subclasses[0]
        try:
            subclass.model_validate(value)
            return True
        except ValidationError:
            return False

    def to_json(self, indent: Optional[int] = None):
        return type(self).model_dump_json(self, indent=indent)

