# Working with References

OpenAPI specifications use references (`$ref`) to avoid duplication and keep schemas manageable. Cicerone provides a comprehensive API for navigating and resolving these references.

## Understanding References in OpenAPI

A reference in OpenAPI uses the `$ref` keyword to point to another part of the specification. References follow the JSON Reference specification (RFC 6901) and use JSON Pointer syntax.

### Reference Types

Cicerone supports several types of references:

1. **Local references** - Point to other parts of the same document
   ```yaml
   $ref: '#/components/schemas/User'
   ```

2. **External references** - Point to other files (coming in future versions)
   ```yaml
   $ref: './models/user.yaml#/User'
   ```

### Reference Locations

References can appear in various places in an OpenAPI specification:

- **Schema objects** - Most common, referencing reusable schemas
- **Response objects** - Referencing reusable responses
- **Parameter objects** - Referencing reusable parameters
- **Request body objects** - Referencing reusable request bodies
- **And more** - Anywhere the spec allows a Reference Object

## Basic Reference Navigation

### Resolving a Reference

The most common operation is resolving a reference to get its target object:

```python
from cicerone import parse as cicerone_parse

# Load your OpenAPI spec
spec = cicerone_parse.parse_spec_from_file('openapi.yaml')

# Resolve a reference to a schema
user_schema = spec.resolve_reference('#/components/schemas/User')
print(f"User schema type: {user_schema['type']}")
print(f"User properties: {list(user_schema['properties'].keys())}")
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
# Resolves to the User schema object
user_schema = spec.resolve_reference('#/components/schemas/User')
# Output: {'type': 'object', 'required': ['id', 'username', 'email'], 'properties': {...}}
```

### Finding All References

You can discover all references in your specification:

```python
# Get all references in the spec
all_refs = spec.get_all_references()

# Filter by type
local_refs = [r for r in all_refs if r.is_local]
external_refs = [r for r in all_refs if r.is_external]

print(f"Found {len(all_refs)} total references")
print(f"Local: {len(local_refs)}, External: {len(external_refs)}")

# List all schema references
schema_refs = [r for r in all_refs if '/schemas/' in r.ref]
for ref in schema_refs:
    print(f"  - {ref.ref}")
```

## Working with the Reference Model

The `Reference` class provides properties to inspect and work with reference objects:

```python
from cicerone.spec import Reference

# Create a reference object
ref = Reference(ref='#/components/schemas/Pet')

# Check reference type
print(f"Is local: {ref.is_local}")  # True
print(f"Is external: {ref.is_external}")  # False

# Get the JSON Pointer
print(f"Pointer: {ref.pointer}")  # /components/schemas/Pet

# Get pointer components
print(f"Parts: {ref.pointer_parts}")  # ['components', 'schemas', 'Pet']
```

### OAS 3.1 Summary and Description

In OpenAPI 3.1, Reference Objects can have `summary` and `description` fields:

```python
ref = Reference(
    ref='#/components/schemas/User',
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
# Returns: {'$ref': '#/components/schemas/Person'}
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
# Check if a reference is circular
is_circular = spec.is_circular_reference('#/components/schemas/Node')
print(f"Is circular: {is_circular}")

# When resolving, circular references are detected
try:
    # This will work for the Node schema itself
    node = spec.resolve_reference('#/components/schemas/Node')
    print("Node schema resolved successfully")
    
    # But attempting to fully resolve a circular chain will raise an error
    # (Only when follow_nested would cause infinite recursion)
except RecursionError as e:
    print(f"Circular reference detected: {e}")
```

### Array Index References

You can use array indices in reference paths:

```yaml
tags:
  - name: users
    description: User operations
  - name: posts
    description: Post operations
```

```python
# Reference by array index
posts_tag = spec.resolve_reference('#/tags/1')
print(f"Tag name: {posts_tag['name']}")  # 'posts'
```

## Practical Examples

### Example 1: Schema Validation

Check if all referenced schemas exist:

```python
spec = cicerone_parse.parse_spec_from_file('openapi.yaml')

# Find all schema references
all_refs = spec.get_all_references()
schema_refs = [r for r in all_refs if '/schemas/' in r.ref]

# Validate each reference
for ref in schema_refs:
    try:
        schema = spec.resolve_reference(ref)
        print(f"✓ {ref.ref} - Valid")
    except ValueError as e:
        print(f"✗ {ref.ref} - Error: {e}")
```

### Example 2: Exploring Response Schemas

Navigate from an operation to its response schema:

```python
# Parse the spec
spec = cicerone_parse.parse_spec_from_file('openapi.yaml')

# Get an operation
operation = spec.operation_by_operation_id('listUsers')

# Check if the operation exists
if operation:
    # Get the 200 response
    if '200' in operation.responses:
        response = operation.responses['200']
        
        # Get the response content
        if 'application/json' in response.content:
            media_type = response.content['application/json']
            
            # Check if the schema is a reference
            from cicerone.spec import Reference
            if Reference.is_reference(media_type.schema):
                # Resolve the reference
                ref_dict = media_type.schema
                schema = spec.resolve_reference(ref_dict['$ref'])
                print(f"Response schema: {schema}")
```

### Example 3: Building a Schema Registry

Create a registry of all schemas with their dependencies:

```python
from cicerone.spec import Reference

spec = cicerone_parse.parse_spec_from_file('openapi.yaml')

# Build a dependency map
schema_deps = {}
for schema_name, schema_obj in spec.components.schemas.items():
    # Find references in this schema
    refs = spec.get_all_references(spec.raw['components']['schemas'][schema_name])
    schema_refs = [r.ref for r in refs if '/schemas/' in r.ref]
    
    # Extract schema names
    dep_names = [ref.split('/')[-1] for ref in schema_refs]
    schema_deps[schema_name] = dep_names

# Print the registry
print("Schema Dependency Registry:")
for schema, deps in schema_deps.items():
    if deps:
        print(f"  {schema} depends on: {', '.join(deps)}")
    else:
        print(f"  {schema} (no dependencies)")
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

Resolve a reference to its target object.

**Parameters:**
- `ref` (str or Reference): Reference to resolve
- `follow_nested` (bool): Whether to recursively resolve nested references

**Returns:** The target object (dict or other type)

**Raises:**
- `ValueError`: If reference cannot be resolved
- `RecursionError`: If circular reference detected

#### `get_all_references()`

Get all references in the specification.

**Returns:** List of Reference objects

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
