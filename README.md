# `camdkit.clip` reimplemented with Pydantic

## TL:DR;

This is nerding out re: code modularity and maintainability. If your RIS
involvement is mostly about "how do I transport this info with ST 2110"
or "how do I process received metadata on hardware that might not even
support floating point", please don't waste time reading this.

## This README.md is a work in progress
I started writing it less than five hours before our next camera tracking
meeting, and am going to commit and push it in chunks so that even if I
don't finish, you can still get the broad outlines.

## Motivation

The road to `camdkit` was long and twisty. Originally its charter was to be a
[Rosetta Stone](https://en.wikipedia.org/wiki/Rosetta_Stone) for diverse camera
and lens metadata, using the bright clarity of an implementation to cut through
the fog of different vendors using the same terms for the semantically same 
thing, or meaning the same thing but describing its states in different units.

Quite deliberately the canonical representation into which all camera and lens
metadata was cast was declared a common working space but _not_ a set of
requirements for transport or storage.

With the exception of the `Dimension` class, all the metadata described were
what one would call POD [Plain Old Data] types. They might be _constrained_ POD
types, such as "non-negative integer", but they were very simple. The classes
that implemented a representation of these types without regard to their use
were named something like PODType`Parameter` and were in `framework.py`; the
uses of those `Parameter`s were in `model.py` and had arbitrary names.

An example will make this more clear. Here is the definition of a parameter to
generically handle strings:
```angular2html
class StringParameter(Parameter):

  @staticmethod
  def validate(value) -> bool:
    """The parameter shall be a Unicode string betwee 0 and 1023
    codepoints.
    """
    return isinstance(value, str) and len(value) < 1024

  @staticmethod
  def to_json(value: typing.Any) -> typing.Any:
    return str(value)

  @staticmethod
  def from_json(value: typing.Any) -> typing.Any:
    return str(value)

  @staticmethod
  def make_json_schema() -> dict:
    return {
      "type": "string",
      "minLength": 1,
      "maxLength": 1023
    }
```
and here is how it would be used in `model.py`:
```angular2html
class LensSerialNumber(StringParameter):
  """Non-blank string uniquely identifying the lens"""

  canonical_name = "serialNumber"
  sampling = Sampling.STATIC
  units = None
  section = "lens"
```

This worked well. But to this developer's eyes, it didn't scale well to when
the metadata set was vastly extended to support camera tracking metadata,
including geometric transform chains, device synchronization, semantic
versioning, &c. For something like a set of 1-3 coefficients representing
exposure falloff, `framework.py` carried those coefficients in a `dataclass`
object:
```angular2html
@dataclasses.dataclass
class ExposureFalloff:
  """Coefficients for the calculation of exposure fall-off"""
  a1: float
  a2: typing.Optional[float] = None
  a3: typing.Optional[float] = None
```
The logic for validation, serialization, and self-describing schema generation
was added not in `framework.py` to the definition of a parameter _type_, but
in `model.py` tied much more closely to the parameter's _use_. Thus in
`model.py` one would have a class built on top of a generic `Parameter`, the
root class for all of `framework.py`'s parameter types:

```angular2html
class LensExposureFalloff(Parameter):
  """Coefficients for calculating the exposure fall-off (vignetting) of
  a lens
  """
  sampling = Sampling.REGULAR
  canonical_name = "exposureFalloff"
  section = "lens"
  units = None

  @staticmethod
  def validate(value) -> bool:
    """The coefficients shall each be real numbers."""

    if not isinstance(value, ExposureFalloff):
      return False
 
    # a1 is required
    if value.a1 == None:
      return False

    for v in [value.a1, value.a2, value.a3]:
      if v is not None and not isinstance(v, numbers.Real):
        return False

    return True

  @staticmethod
  def to_json(value: typing.Any) -> typing.Any:
    return dataclasses.asdict(value)

  @staticmethod
  def from_json(value: typing.Any) -> typing.Any:
    return ExposureFalloff(**value)

  @staticmethod
  def make_json_schema() -> dict:
    return &#123;
      "type": "object",
      "additionalProperties": False,
      "required": ["a1"],
      "properties": {
        "a1": {
            "type": "number"
        },
        "a2": {
            "type": "number"
        },
        "a3": {
            "type": "number"
        }
      }
    }

```

To rigidly maintain the original functional division between `framework.py` 
and `model.py` one would need to define an elaborate `Parameter` subclass
type in `framework.py` and then one could tersely use it in `model.py` in
the "original style" of `camdkit`.

But this could often seem very artificial
and a lot of work, given that these new parameter types and parameters always
had a 1:1 relationship, _vs._ the 1:n relationship between `StringParameter`
in `framework.py` for example and its multipicity of uses (`CameraMake`,
`LensModel`, &c) in `model.py`.

The now-diffused responsibility required the maintainer to make more choices
than they had previously needed to make.

