# Compatibility & Testing

Cicerone is rigorously tested to work with real-world OpenAPI schemas. 

We use multiple layers of testing to validate compatibility across a wide range of specifications.

## Testing Strategy

Our testing combines unit tests, integration tests, and large-scale compatibility testing.

### Unit Tests

The test suite includes comprehensive unit tests for individual components:

- **Parser functions**: Testing all input formats (files, URLs, dicts, JSON, YAML)
- **Schema models**: Validating Pydantic model behavior and field handling
- **References**: Testing `$ref` resolution and circular reference handling
- **Components**: Verifying proper parsing of schemas, parameters, responses, etc.
- **OpenAPI features**: Testing callbacks, webhooks, security schemes, and extensions

These tests ensure that each piece of Cicerone works correctly in isolation.

### Real-World Schema Tests

We maintain a collection of real-world OpenAPI schemas from popular APIs to test against:

- **Ably** - Event streaming API (OpenAPI 3.0.1)
- **Twilio** - Communications API (OpenAPI 3.0.1)
- **1Password** - Security and secrets management (OpenAPI 3.0.0)
- **Google** - Cloud services APIs (OpenAPI 3.0.0)
- **SpaceTraders** - Game API (OpenAPI 3.0.0)
- **Adyen** - Payment platform with OpenAPI 3.1 features (OpenAPI 3.1.0)

These schemas cover a wide range of features and edge cases found in production APIs.

### OpenAPI Directory Compatibility Testing

To ensure broad compatibility, Cicerone is tested against the entire [APIs.guru OpenAPI Directory](https://github.com/APIs-guru/openapi-directory)—a massive collection of 4000+ real-world OpenAPI schemas from hundreds of APIs.

This testing happens automatically:

- **Weekly CI runs**: Every Monday, GitHub Actions runs the test suite against all schemas
- **Manual testing**: Developers can run compatibility tests locally
- **Continuous monitoring**: The test results are tracked to catch regressions

#### Running Compatibility Tests

You can run the compatibility tests yourself:

```bash
# Test against all schemas (takes several minutes)
make test-openapi-directory

# Test a limited subset for quick feedback
python3 test_openapi_directory.py --limit 100

# Stop on first failure for debugging
python3 test_openapi_directory.py -x

# Keep the cloned repository for inspection
python3 test_openapi_directory.py --keep-repo
```

#### Current Results

As of the latest test run, Cicerone successfully parses **98.72%** of schemas in the OpenAPI Directory:

```sh
================================================================================
SUMMARY
================================================================================
Total schemas tested: 4138
Successful: 4085
Failed: 53
Success rate: 98.72%

53 schemas failed to parse:
  - APIs/akeneo.com/1.0.0/swagger.yaml
  - APIs/apidapp.com/2019-02-14T164701Z/openapi.yaml
  - APIs/atlassian.com/jira/1001.0.0-SNAPSHOT/openapi.yaml
  - APIs/azure.com/cognitiveservices-LUIS-Authoring/2.0/swagger.yaml
  - APIs/azure.com/cognitiveservices-LUIS-Authoring/3.0-preview/swagger.yaml
  - APIs/azure.com/cognitiveservices-LUIS-Programmatic/v2.0/swagger.yaml
  - APIs/azure.com/network-applicationGateway/2015-06-15/swagger.yaml
  - APIs/azure.com/network-applicationGateway/2016-09-01/swagger.yaml
  - APIs/azure.com/network-applicationGateway/2016-12-01/swagger.yaml
  - APIs/azure.com/network-applicationGateway/2017-03-01/swagger.yaml
  ... and 43 more
```

**Note**: Most of these failures are due to malformed content in the schema files themselves.

## OpenAPI Version Support

Cicerone fully supports both major OpenAPI 3.x versions:

### OpenAPI 3.0.x

Full support for all OpenAPI 3.0 features:

- ✅ Path operations (GET, POST, PUT, DELETE, etc.)
- ✅ Request and response schemas
- ✅ Parameters (path, query, header, cookie)
- ✅ Components (schemas, parameters, responses, examples, etc.)
- ✅ Security schemes (apiKey, http, oauth2, openIdConnect)
- ✅ Callbacks
- ✅ Server variables
- ✅ Extensions (x-* fields)

### OpenAPI 3.1.x

Full support for OpenAPI 3.1 additions:

- ✅ Webhooks
- ✅ JSON Schema 2020-12 compatibility
- ✅ Nullable types via array syntax: `type: ['string', 'null']`
- ✅ `jsonSchemaDialect` field
- ✅ Updated schema vocabulary

## Known Limitations

Cicerone is designed to parse and represent OpenAPI schemas, not validate them. Here are some edge cases to be aware of:

### Invalid Schemas

Cicerone will attempt to parse malformed schemas but may fail on:

- **Malformed YAML/JSON**: Syntax errors in the underlying format
- **Invalid timestamps**: Non-standard date/time values in the schema metadata
- **Circular references**: Some deeply nested circular `$ref` patterns may cause issues

### Validation

Cicerone parses schemas into Python objects but doesn't validate that they conform to the OpenAPI specification. If you need strict validation, use a dedicated OpenAPI validator before using Cicerone.

## Continuous Improvement

We're constantly improving compatibility:

- **New schemas**: As we discover edge cases, we add them to our test fixtures
- **Bug fixes**: GitHub Issues and PRs help us identify and fix compatibility problems
- **Feature requests**: We track OpenAPI specification updates and add support for new features

If you encounter a schema that Cicerone can't parse, please [open an issue](https://github.com/phalt/cicerone/issues) with the schema or a link to it.

## See Also

- [Parser API](parser.md) - Loading specifications from different sources
- [Working with References](references.md) - Resolving `$ref` references
- [Models](models.md) - Understanding the OpenAPI object models
