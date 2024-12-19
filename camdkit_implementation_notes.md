# Notes on implementing a plug-compatible `Clip.py` replacement

The basic responsibilities of a `Parameter` were fourfold:
```python
class Parameter:
  """Metadata parameter base class"""

  @staticmethod
  def validate(value) -> bool:
    raise NotImplementedError

  @staticmethod
  def to_json(value: typing.Any) -> typing.Any:
    raise NotImplementedError

  @staticmethod
  def from_json(value: typing.Any) -> typing.Any:
    raise NotImplementedError

  @staticmethod
  def make_json_schema() -> dict:
    raise NotImplementedError
```
## The Big Four

- validate

Parameter containers can be serialized to and deserialized from JSON, and they can generate a schema for the container:
  The `to_json()` method iterates over the `_params` class variable, and builds up content either once as `obj["static"][<section>][<canonical_name>]` or `obj[<section>][<canonical_name>]`. The value of the content is produced by the `to_json()` method of the descriptor for the parameter. When the parameter isn't associated with any section, it's inserted either as `obj["static"][<canonical_name>]` or `obj[<canonical_name>]`. What is finally returned is a JSON dict, not a JSONified string.

  The `from_json()` method takes a JSON dict and recursively loads first the static section, and then (in what looks like an O(n^2) fashion) for each non-static section it iterates through all possible items, and if ... whatever, let's trust it for now.

  The `make_json_schema()` class method starts out with some boilerplate identifying the schema, then basically iterates over all the parameters. There are two outer-level cases: the attribute belongs to a section, or it doesn't.
  - If it does belong to a section, then there are two possibilities: either the attribute is static, or it's regularly sampled. The former go into `schema["properties"]["static"]["properties"][<section>]["properties"][<canonical_name>]` with three elements: the schema for the parameter, the parameter description, and the parameter units; the latter, much the same except for the leading `["properties"]["static"]` levels.
  - If it doesn't belong to a section, the situation is analogous.

  The `make_documentation` class method iterates over all the parameters, making a list of dicts with things such as python name, canonical name, etc. This pulls information out of the docstrings of the parameters and out of the docstrings of the validation method.
  ** We'll need a way to express the constraints when defining BaseModel subclasses; wonder if there's anything on the net that does that automatically for annotations?

Then there's what's needed to make a parameter container iterable. The parameter container relies on the subclass to provide an `__item__()`` method.
  ** two potential issues:
    - because the modification and restoration of the sampling state of all the parameters is wholesale, static parameters will be marked as sampled parameters at the end of iteration.
    - because what's being bashed is the static vs. sampled attribute of the parameters stored in the class, it's almost certainly not thread-safe

- model.py
   - that established camera-and-lens-semantically-significant metadata by subclassing the various Parameter subclasses, and adding four class variables to each: canonical_name, sampling, units and section

========


ProjectionOffset and DistortionOffset should share code cleanly



### Suppressed warnings
# See this for a discussion of why #noexception PyNestedDecorators is used above field decorators
https://youtrack.jetbrains.com/issue/PY-34368/False-warning-This-decorator-will-not-receive-a-callable-it-may-expect-when-classmethod-is-not-the-last-applied

Note that for some reason our ability to use the compatibility classmethod from_json requires `__init__` argument names to match the aliases we use for validation, which is counterintuitive

### notes from test_model.py
Changes:

test_serialize():
distinguish between physical and sensel dimensions; the old code did not.

test_active_sensor_physical_dimensions()
use PhysicalDimensions, not Dimensions

test_active_sensor_resolution()
use SenselResolution, not Dimensions

test_duration()
compare result of assignment to StrictlyPositiveRational

test_duration_fraction()
same

test_f_number()
commented out what looks like detection of assigning a list to a tuple attribute

test_t_number()
same as test_f_number()


