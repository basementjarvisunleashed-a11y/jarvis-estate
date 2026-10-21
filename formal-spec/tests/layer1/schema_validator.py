"""Phase 2, Layer 1 — minimal JSON Schema validator (draft-07 subset).

Stdlib-only; supports exactly the keywords used by the v0.1 contract
schemas under contracts/*.schema.json: type, required, additionalProperties,
properties, enum, pattern, minimum, maximum, format (date-time), items.
Meta keywords ($schema, $id, $comment, title, description, version) are
ignored. Any unknown construct fails closed.
"""

import re

_ISO_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$"
)

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
}


class SchemaError(Exception):
    """Raised when an instance violates the schema. Message names the path."""


def _fail(path, reason):
    raise SchemaError("%s: %s" % (path or "$", reason))


def validate(schema, instance, path="$"):
    """Validate instance against schema; raise SchemaError on any violation."""
    if not isinstance(schema, dict):
        _fail(path, "schema is not an object")

    stype = schema.get("type")
    if stype is not None:
        checker = _TYPE_CHECKS.get(stype)
        if checker is None:
            _fail(path, "unknown type keyword %r" % stype)
        if not checker(instance):
            _fail(path, "expected %s, got %s" % (stype, type(instance).__name__))
    elif "enum" not in schema and "properties" not in schema and "items" not in schema:
        # A schema with no validation keywords at all is a hole; fail closed.
        _fail(path, "empty schema (no validation keywords)")

    if "enum" in schema and instance not in schema["enum"]:
        _fail(path, "value %r not in enum %r" % (instance, schema["enum"]))

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for field in required:
            if field not in instance:
                _fail(path, "missing required field %r" % field)
        props = schema.get("properties", {})
        for key, value in instance.items():
            if key in props:
                validate(props[key], value, "%s.%s" % (path, key))
            elif schema.get("additionalProperties") is False:
                _fail(path, "additional property %r not allowed" % key)

    if isinstance(instance, list) and "items" in schema:
        items = schema["items"]
        for i, value in enumerate(instance):
            validate(items, value, "%s[%d]" % (path, i))

    if isinstance(instance, str):
        pattern = schema.get("pattern")
        if pattern is not None and not re.search(pattern, instance):
            _fail(path, "value %r does not match pattern %r" % (instance, pattern))
        fmt = schema.get("format")
        if fmt == "date-time" and not _ISO_DATETIME.match(instance):
            _fail(path, "value %r is not a date-time" % instance)

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            _fail(path, "value %r below minimum %r" % (instance, minimum))
        maximum = schema.get("maximum")
        if maximum is not None and instance > maximum:
            _fail(path, "value %r above maximum %r" % (instance, maximum))

    return True
