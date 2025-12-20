# Working with References

OpenAPI specifications use references (`$ref`) to avoid duplication and keep schemas manageable. Cicerone provides a comprehensive API for navigating and resolving these references.

## Understanding References in OpenAPI

A reference in OpenAPI uses the `$ref` keyword to point to another part of the specification. References follow the JSON Reference specification (RFC 6901) and use JSON Pointer syntax.

### Reference Locations

References can appear in various places in an OpenAPI specification:

- **Schema objects** - Most common, referencing reusable schemas
- **Response objects** - Referencing reusable responses
- **Parameter objects** - Referencing reusable parameters
- **Request body objects** - Referencing reusable request bodies
- **And more** - Anywhere the spec allows a Reference Object

## Basic Reference Navigation

### Resolving a Reference

The most common operation is resolving a reference to get its target object as a typed Pydantic model:

```python
from cicerone import parse as cicerone_parse
from cicerone.spec import Schema

# Load your OpenAPI spec
spec = cicerone_parse.parse_spec_from_file('openapi.yaml')

# Resolve a reference to a schema - returns a Schema object, not a dict
user_schema = spec.resolve_reference('#/components/schemas/User')
print(f"Type: {type(user_schema)}")  # <class 'cicerone.spec.schema.Schema'>
print(f"User schema type: {user_schema.type}")
print(f"User properties: {list(user_schema.properties.keys())}")
```

Example with a sample schema:

```yaml
components:
  schemas:
    User:
      type: object
      required:
        - id
        - username
        - email
      properties:
        id:
          type: string
        username:
          type: string
        email:
          type: string
          format: email
```

```python
# Resolves to a typed Schema object
user_schema = spec.resolve_reference('#/components/schemas/User')
assert isinstance(user_schema, Schema)
# Access properties directly as attributes
print(user_schema.type)  # 'object'
print(user_schema.required)  # ['id', 'username', 'email']
print(user_schema.properties['email'].format)  # 'email'
```

### Finding All References

You can discover all references in your specification as a dictionary:

```python
# Get all references as a dict mapping $ref strings to Reference objects
all_refs = spec.get_all_references()

# Access specific references by their $ref string
user_ref = all_refs.get('#/components/schemas/User')
if user_ref:
    print(f"Found reference: {user_ref.ref}")

# Filter by type
local_refs = {k: v for k, v in all_refs.items() if v.is_local}
external_refs = {k: v for k, v in all_refs.items() if v.is_external}

print(f"Found {len(all_refs)} total references")
print(f"Local: {len(local_refs)}, External: {len(external_refs)}")

# List all schema references
schema_refs = {k: v for k, v in all_refs.items() if '/schemas/' in k}
for ref_str, ref_obj in schema_refs.items():
    print(f"  - {ref_str}")
```

## Working with the Reference Model

The `Reference` class provides properties to inspect and work with reference objects:

```python
from cicerone.references import Reference
from cicerone.spec import Schema

# Create a reference object
ref = Reference(ref='#/components/schemas/Pet')

# Check reference type
print(f"Is local: {ref.is_local}")  # True
print(f"Is external: {ref.is_external}")  # False

# Get the JSON Pointer
print(f"Pointer: {ref.pointer}")  # /components/schemas/Pet

# Get pointer components
print(f"Parts: {ref.pointer_parts}")  # ['components', 'schemas', 'Pet']

# Resolve the reference to get the actual Schema object
pet_schema = spec.resolve_reference(ref)
assert isinstance(pet_schema, Schema)
print(f"Pet schema type: {pet_schema.type}")
```

### OAS 3.1 Summary and Description

In OpenAPI 3.1, Reference Objects can have `summary` and `description` fields:

```python
from cicerone.references import Reference

ref = Reference(ref='#/components/schemas/User',
    summary='User schema',
    description='Represents a user in the system'
)

print(f"Reference: {ref.ref}")
print(f"Summary: {ref.summary}")
print(f"Description: {ref.description}")
```

## Advanced Reference Operations

### Nested References

Cicerone can automatically follow nested references:

```yaml
components:
  schemas:
    UserList:
      type: array
      items:
        $ref: '#/components/schemas/User'
    User:
      $ref: '#/components/schemas/Person'
    Person:
      type: object
      properties:
        name:
          type: string
```

```python
# By default, follows nested references
person = spec.resolve_reference('#/components/schemas/User')
# Returns the Person schema (fully resolved)

# Or stop at the first level
user_ref = spec.resolve_reference('#/components/schemas/User', follow_nested=False)
```

### Circular Reference Detection

Some schemas have circular references (e.g., tree structures):

```yaml
components:
  schemas:
    Node:
      type: object
      properties:
        value:
          type: string
        children:
          type: array
          items:
            $ref: '#/components/schemas/Node'  # Circular!
```

Cicerone detects and handles circular references:

```python
from cicerone.references import ReferenceResolver

# Check if a reference is circular
resolver = ReferenceResolver(spec)
is_circular = resolver.is_circular_reference('#/components/schemas/Node')
print(f"Is circular: {is_circular}")

# When resolving with follow_nested=True, circular references are handled
# by stopping recursion - the circular reference remains as a Reference object
# pointing back to create a linked-list style structure
node = spec.resolve_reference('#/components/schemas/Node', follow_nested=True)
print("Node schema resolved successfully with circular handling")
```

## Reference Resolution Rules

### OAS 3.0 vs 3.1 Differences

The behavior of references differs slightly between OpenAPI versions:

**OpenAPI 3.0:**

- Reference Objects can only contain `$ref`
- Adjacent keywords are ignored
- References fully replace the object

**OpenAPI 3.1:**

- Reference Objects can have `summary` and `description`
- These fields override the target's values
- In Schema Objects, `$ref` can coexist with other keywords (acts like `allOf`)

Cicerone handles both versions correctly, preserving the raw specification data.

## API Reference

### OpenAPISpec Methods

#### `resolve_reference(ref, follow_nested=True)`

Resolve a reference to its target object as a typed Pydantic model.

**Parameters:**

- `ref` (str or Reference): Reference to resolve
- `follow_nested` (bool): Whether to recursively resolve nested references

**Returns:** Typed Pydantic model (Schema, Response, Parameter, etc.) when the reference points to a recognized component type. Otherwise returns raw data.

**Raises:**

- `ValueError`: If reference cannot be resolved
- `RecursionError`: If circular reference detected

#### `get_all_references()`

Get all references in the specification.

**Returns:** Dictionary mapping $ref strings to Reference objects

**Example:**

```python
all_refs = spec.get_all_references()
user_ref = all_refs.get('#/components/schemas/User')
local_refs = {k: v for k, v in all_refs.items() if v.is_local}
```

#### `is_circular_reference(ref)`

Check if a reference creates a circular dependency.

**Parameters:**

- `ref` (str or Reference): Reference to check

**Returns:** bool - True if circular

### Reference Class

#### Properties

- `ref` (str): The reference string
- `summary` (str | None): Summary (OAS 3.1+)
- `description` (str | None): Description (OAS 3.1+)
- `is_local` (bool): True if local reference (#...)
- `is_external` (bool): True if external reference
- `pointer` (str): JSON Pointer part (/components/schemas/User)
- `document` (str): Document part (for external refs)
- `pointer_parts` (list[str]): Pointer split into components

#### Methods

- `from_dict(data)`: Create from dictionary
- `is_reference(data)`: Check if data contains $ref

## Best Practices

1. **Check for references before accessing**: Use `Reference.is_reference()` to check if an object is a reference
2. **Handle circular references gracefully**: Use `is_circular_reference()` before full resolution
3. **Cache resolved references**: If resolving the same reference multiple times, cache the results
4. **Validate references**: Check that all references in your spec can be resolved

## Limitations

Current limitations (to be addressed in future versions):

- External references (file paths, URLs) are not yet supported
- `operationRef` in Link Objects is not yet implemented
- `mapping` in Discriminator Objects is not yet implemented
- Dynamic references (`$dynamicRef`) from JSON Schema 2020-12 / OAS 3.1 are not yet supported

## See Also

- [OpenAPI Reference Object Specification](https://spec.openapis.org/oas/v3.1.0#reference-object)
- [JSON Pointer RFC 6901](https://datatracker.ietf.org/doc/html/rfc6901)
- [JSON Reference Draft](https://datatracker.ietf.org/doc/html/draft-pbryan-zyp-json-ref-03)
