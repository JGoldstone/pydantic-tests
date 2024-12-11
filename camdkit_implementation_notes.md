camdkit implementation notes

My issues are these:
- the original structure worked for normalizing simple atomic metadata from cameras and lenses; it has not stood up well under the added weight of carrying attributes that are aggregates of simple atomic metadata.
- hand-crafting JSON schema is potentially error-prone and if the schema can be constructed by introspection, that is a more maintainable approach
- Python's "don't repeat yourself" principle is violated when every parameter that is based on a Rational or that uses a Rational has to hand-code the same JSON to represent that Rational, rather than somehow re-using a single schema that is generated as part of the definition of a reusable Rational component
- 

How it came to this

The original code had
- framework.py
  - that established a set of Parameter subclasses that handled primitive types, and nothing but. The sole exception was the DimensionsParameter subclass of Parameter, which was closely tied to a dataclass in that same file, with two members, each of type numbers.Real. Basically, though, the definitions in framework.py were very generic.
  - that defined a ParameterContainer class, on which model.py would be based.

  ParameterContainer has the following instance attribute:
    `_values`, an untyped dict

  Clip has the following class attribute:
    `_params`, an untyped dict

  A new clip is initialized like this:
    The definition of `Clip` is read in when `models.py` is loaded, and class attributes, one per parameter
      that the clip stores, are initialized to the results of no-argument invocations of each parameter
    The `__subclass_init__()` for `Clip'`s parent (i.e. `ParameterContainer`) is called, with the `Clip` class object
      as its sole argument. It initializes a `_params` class variable to an empty dict, then iterates over `Clip`'s attributes, both callable and non-callable:
        - all the basic dunder methods from `Object`
        - the `_changed_sampling` class variable from `Clip`
        - the `_params` class variable it just defined in `Clip`
        - the `_reset_sampling` method of `Clip`
        - the `_set_regular` and `_set_static methods` of `Clip`
        - the class attributes holding parameters in `Clip`, whose values are no-arg constructor results
        - misc other `Clip`-defined methods: `append`, `validate`
        - misc other `ParameterContainer`-defined methods: `from_json`, `to_json`, `make_json_schema`, `make_documentation`
      If the attribute is a subclass of `Parameter`, it is checked to verify that the given subclass has defined class variables for `canonical_name`, `sampling`, and `units`; if not we skip what's below and keep iterating.
      The value of the attribute (which will have class attributes for `canonical_name`, `sampling` and `units`) is inserted into the `_params` class variable for `Clip`
      The value of the attribute is changed to be a descriptor (created with `property`) which implements a getter and a setter that keys into the instance's `_values` instance attribute by attribute name
      The `__init__()` method for `Clip` is replaced with a method that
      - calls the `__init__()`` methods of all bases of `Clip` (or a subclass of `Clip`)
      - calls `ParameterContainer`'s `Clip`
      - calls `Clip'`s `__init__()``
      - ...which I think means for the simple case of `Clip` rather than some subclass of `Clip`, `ParameterContainer`'s `__init__()` gets called three times
    Basically this is all about setting up attributes as super-properties, which do extra validation: if the attribute represents regular samples, then before its value is replaced (or initially set), that value is checked to verify that yes, it's a tuple and yes, every type member passes validation.

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

The problem with camdkit modularity can be seen by looking at the make_json_schema() method of TimingSynchronization: it has to hand-code the definition of a Rational as part of its JSON

Also ProjectionOffset and DistortionOffset should share code cleanly

=== Things to investigate
Can one validate an empty clip?
Shouldn't there be a check that any parameter has a 'section' class attribute?

Suppose you have a clip with REGULAR parameters a, b and c, seven samples each
Now append a clip with REGULAR parameters a, b and d, four samples each
What happens when you want the 9th c?
What happens when you want the second d?

Here is how accessing a single frame at index i works...
Make a new clip
Go over all the attributes of the original clip
  if an attribute is a parameter
    if that parameter is regular
      temporarily change the parameter descriptor in the original clip to be static
      set the new clip's value for that attribute to be the descriptor at i (desc[i]) ?? <- what?
      note in the original clip that the parameter descriptor was changed to be static
    else
      set the new clip's descriptor for that attribute to be descriptor
