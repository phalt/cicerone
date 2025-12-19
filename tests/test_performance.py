"""Performance benchmarks for OpenAPI spec parsing and traversal."""

from __future__ import annotations

import pathlib

import pytest

from cicerone import parse as cicerone_parse


class TestPerformance:
    """Performance benchmark tests."""

    @pytest.fixture
    def petstore_spec_path(self):
        """Path to simple petstore spec."""
        return pathlib.Path(__file__).parent / "fixtures" / "petstore_openapi3.yaml"

    @pytest.fixture
    def complex_spec_path(self):
        """Path to complex spec."""
        return pathlib.Path(__file__).parent / "fixtures" / "complex_api.yaml"

    def test_parse_simple_spec_performance(self, benchmark, petstore_spec_path):
        """Benchmark parsing a simple OpenAPI spec."""
        result = benchmark(cicerone_parse.parse_spec_from_file, petstore_spec_path)
        assert result.version.major == 3

    def test_parse_complex_spec_performance(self, benchmark, complex_spec_path):
        """Benchmark parsing a complex OpenAPI spec with many paths and schemas."""
        result = benchmark(cicerone_parse.parse_spec_from_file, complex_spec_path)
        assert result.version.major == 3
        # Verify it parsed all the data
        assert len(result.paths.items) >= 70
        assert len(result.components.schemas) >= 100

    def test_traverse_all_operations_performance(self, benchmark, complex_spec_path):
        """Benchmark traversing all operations in a complex spec."""
        spec = cicerone_parse.parse_spec_from_file(complex_spec_path)

        def traverse_operations():
            return list(spec.all_operations())

        result = benchmark(traverse_operations)
        # Should have multiple operations per path
        assert len(result) >= 200

    def test_find_operation_by_id_performance(self, benchmark, complex_spec_path):
        """Benchmark finding an operation by operationId."""
        spec = cicerone_parse.parse_spec_from_file(complex_spec_path)

        def find_operation():
            return spec.operation_by_operation_id("getResource25")

        result = benchmark(find_operation)
        assert result is not None
        assert result.operation_id == "getResource25"

    def test_access_nested_schema_properties_performance(self, benchmark, complex_spec_path):
        """Benchmark accessing nested schema properties."""
        spec = cicerone_parse.parse_spec_from_file(complex_spec_path)

        def access_schema():
            schema = spec.components.get_schema("Resource10")
            if schema:
                # Access nested properties
                _ = list(schema.properties.keys())
                if "metadata" in schema.properties:
                    _ = list(schema.properties["metadata"].properties.keys())
            return schema

        result = benchmark(access_schema)
        assert result is not None

    def test_iterate_all_schemas_performance(self, benchmark, complex_spec_path):
        """Benchmark iterating through all schemas."""
        spec = cicerone_parse.parse_spec_from_file(complex_spec_path)

        def iterate_schemas():
            schemas = []
            for name, schema in spec.components.schemas.items():
                schemas.append((name, schema.type, len(schema.properties)))
            return schemas

        result = benchmark(iterate_schemas)
        assert len(result) >= 100


class TestScalability:
    """Test scalability with various spec sizes."""

    @pytest.fixture
    def complex_spec_path(self):
        """Path to complex spec."""
        return pathlib.Path(__file__).parent / "fixtures" / "complex_api.yaml"

    def test_large_spec_operations_count(self, complex_spec_path):
        """Verify we can handle specs with many operations."""
        spec = cicerone_parse.parse_spec_from_file(complex_spec_path)
        operations = list(spec.all_operations())

        # Should handle 200+ operations efficiently
        assert len(operations) >= 200

        # All operations should be accessible
        for op in operations:
            assert op.method is not None
            assert op.path is not None

    def test_large_spec_schemas_count(self, complex_spec_path):
        """Verify we can handle specs with many schemas."""
        spec = cicerone_parse.parse_spec_from_file(complex_spec_path)

        # Should handle 100+ schemas
        assert len(spec.components.schemas) >= 100

        # All schemas should be accessible
        for name, schema in spec.components.schemas.items():
            assert schema.type is not None

    def test_operation_lookup_efficiency(self, complex_spec_path):
        """Test operation lookup remains efficient with many operations."""
        spec = cicerone_parse.parse_spec_from_file(complex_spec_path)

        # Should find operations regardless of position
        first_op = spec.operation_by_operation_id("getResource0")
        middle_op = spec.operation_by_operation_id("getResource25")
        last_op = spec.operation_by_operation_id("getResource49")

        assert first_op is not None
        assert middle_op is not None
        assert last_op is not None
