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
types, such as "non-negative integer", but they were very simple.

### Weakened functional division between two key Python modules
The classes
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

### JSON schema consistency

As `framework.py` and `model.py` currently stand, the schema describing a
parameter is hand-coded as part of the definition of the underlying parameter
type or of the parameter itself. The schema needs to be complete, that is,
it needs to be expanded "all the way down".

When there are multiple parameters that have elements of the same parameter
type, sometimes the existing code can take care of this expansion, but other
times the expansion ends up being done manually. Take this code fragment from
`Transforms.make_json_schema()`, for example:

```angular2html
          "id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1023
          },
          "parentId": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1023
          }
```

That's the representation of a non-blank string no longer than 1023 characters,
a very common element to parameters that aggregate POD parameters or other 
aggregating parameters. And yet that JSON schema has already been defined
elsewhere: this is `StringParameter.make_json_schema` from `framework.py`:

```angular2html
  @staticmethod
  def make_json_schema() -> dict:
    return {
      "type": "string",
      "minLength": 1,
      "maxLength": 1023
    }
```

This is at odds with the Python DRY ("Don't repeat yourself") philosophy. It's
not like there are Python police (well, not yet) that are going to levy a fine on
us for repeating ourselves but still. If we decided we needed to limit the maximum
length to 511 bytes, we would need to change all relevant occurences of 1023,
_vs._ changing it in one place.

Plus, it's _hard_ to hand-code JSON schema. So far we have been good, I think, but
if we are to start adding even more structures, either to define things like 
transport mechanisms, or more likely, to formalize the notion of "Sample", the
schema could get more complex. I've heard others bring this up; it's not just me.

## So what's Pydantic and why is it relevant?

Pydantic (website here) is a "data validation library for Python". It calls 
aggregated structures _models_, which it says are "... similar to structs in
languages like C ...". Its models (built on `pydantic.Basemodel`) aggregate
POD types or other aggregates of POD types, and provide _validation_,
_serialization_ (i.e. conversion to JSON), _deserialization_ (initialization 
from JSON), and JSON _schema generation_.

This can lead to more compact and maintainable code. Picking a not atypical
case from `model.py`:

```angular2html
class Protocol(Parameter):
  """Name of the protocol in which the sample is being employed, and
  version of that protocol
  """
  canonical_name = "protocol"
  sampling = Sampling.REGULAR
  units = None

  @staticmethod
  def validate(value) -> bool:
    """Protocol name is nonblank string; protocol version is basic x.y.z
     semantic versioning string
     """

    if not isinstance(value, VersionedProtocol):
      return False

    if not isinstance(value.name, str):
      return False
    if not len(value.name):
      return False
    if value.name != OPENTRACKIO_PROTOCOL_NAME:  # Temporary restriction
      return False

    if not isinstance(value.version, tuple):
      return False
    if len(value.version) != 3:
      return False
    return all([
      isinstance(version_number_component, int) \
                and version_number_component >= 0 \
                and version_number_component <= 9 \
                for version_number_component in value.version])

  @staticmethod
  def to_json(value: typing.Any) -> typing.Any:
    return {k: v for k, v in dataclasses.asdict(value).items() if v is not None}

  @staticmethod
  def from_json(value: typing.Any) -> typing.Any:
    return VersionedProtocol(**value)

  @staticmethod
  def make_json_schema() -> dict:
    return {
      "type": "object",
      "additionalProperties": False,
      "properties": {
        "name": {
          "type": "string",
            "minLength": 1,
            "maxLength": 1023
        },
        "version": {
          "type": "array",
          "items": {
            "type": "integer",
            "minValue": 0,
            "maxValue": 9
          },
          "minItems": 3,
          "maxItems": 3
        }
      }
    }
```

In the re-implementation of `framework.py` and `model.py` the same parameter
is defined with:

```angular2html
class VersionedProtocol(CompatibleBaseModel):
    name: NonBlankUTF8String
    version: tuple[int, int, int]

    def __init__(self, name: NonBlankUTF8String, version: tuple[SingleDigitInt, SingleDigitInt, SingleDigitInt]):
        super(VersionedProtocol, self).__init__(name=name, version=version)
        if name != OPENTRACKIO_PROTOCOL_NAME:
            raise ValueError("The only currently accepted name for a versioned protocol"
                             " is {OPENTRACKIO_PROTOCOL_NAME}")

```

For the record, the complete definitions of `NonBlankUTF8String` and
`SingleDigitInt` are:

```angular2html
type NonBlankUTF8String = Annotated[str, StringConstraints(min_length=1, max_length=1023)]
```
and
```angular2html
type SingleDigitInt = Annotated[int, Field(..., ge=0, le=9, strict=True)]
```
respectively.

### How does it _do_ that?

Pydantic is built on type hints. Deeply, deeply built on type hints. To make
this reimplementation of `framework.py` and `clip.py` work, one needs to read
up on type hints. I read up on type hints a lot. They are pretty clear in what
they mean; but syntactically, learning about them is a chore. Fortunately, 
there's enough of a variety of examples in the new code so that in the future,
type hinting can almost always be guided by precedent.

Much of the type hinting mechanism is in base Python already, if one is running
semi-modern Python. I believe what's required came in around Python 3.9. I'm
running 3.13; the [VFX reference platform](https://vfxplatform.com) is at 3.11.

A really nice thing is that modern IDEs like Visual Studio Code and PyCharm
understand type hints _deeply_ and while you are coding, you'll get immediate
feedback -- it's validate-as-you-go. If I type
```angular2html
foo = VersionedProtocol("bar", (1, 2, 10))
```
then my IDE is going to flag that 10 as invalid within a fraction of a second
of my typing it.

### What are some downsides?

