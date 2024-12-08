from typing import Final, Annotated
from pydantic import Field, StringConstraints

from camdkit.backwards import CompatibleBaseModel

__all__ = ['Rational', 'StrictlyPositiveRational', 'NonBlankUTF8String']

MIN_UINT_32: Final[int] = 0
MAX_UINT_32: Final[int] = 2**32-1
MIN_INT_32: Final[int] = -2**31
MAX_INT_32: Final[int] = 2**31-1

# init methods because by default Pydantic BaseModel doesn't let you use positional arguments


class Rational(CompatibleBaseModel):
    numerator: int = Field(..., ge=MIN_INT_32, le=MAX_INT_32)
    denominator: int = Field(..., gt=0, le=MAX_UINT_32)

    def __init__(self, n: int, d: int) -> None:
        super(Rational, self).__init__(numerator=n, denominator=d)


class StrictlyPositiveRational(CompatibleBaseModel):
    numerator: int = Field(..., gt=0, le=MAX_INT_32)
    denominator: int = Field(..., gt=0, le=MAX_UINT_32)

    def __init__(self, n: int, d: int, ) -> None:
        super(StrictlyPositiveRational, self).__init__(numerator=n, denominator=d)


class NonBlankUTF8String(CompatibleBaseModel):
    value: Annotated[str, StringConstraints(min_length=1, max_length=1023)]

    def __init__(self, v: str) -> None:
        super(NonBlankUTF8String, self).__init__(value=v)
