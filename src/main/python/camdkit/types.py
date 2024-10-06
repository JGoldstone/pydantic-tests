from typing import Final
from pydantic import BaseModel, Field

MIN_UINT_32: Final[int] = 0
MAX_UINT_32: Final[int] = 2**32-1
MIN_INT_32: Final[int] = -2**31
MAX_INT_32: Final[int] = 2**31-1

# init method because by default Pydantic BaseModel doesn't let you use positional arguments


class Rational(BaseModel):
    numerator: int = Field(..., ge=MIN_INT_32, le=MAX_INT_32)
    denominator: int = Field(..., gt=0, le=MAX_UINT_32)
    def __init__(self, n: int, d: int, **kwargs) -> None:
        super(Rational, self).__init__(numerator=n, denominator=d, **kwargs)


class StrictlyPositiveRational(BaseModel):
    numerator: int = Field(..., gt=0, le=MAX_INT_32)
    denominator: int = Field(..., gt=0, le=MAX_UINT_32)
    def __init__(self, n: int, d: int, **kwargs) -> None:
        super(StrictlyPositiveRational, self).__init__(numerator=n, denominator=d, **kwargs)


class NonBlankUTF8String(BaseModel):
    value: str = Field(min_length=1, max_length=1023)
    def __init__(self, v: str, **kwargs) -> None:
        super(NonBlankUTF8String, self).__init__(value=v, **kwargs)
