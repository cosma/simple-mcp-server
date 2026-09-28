#!/usr/bin/env python3
"""Test suite for MCP server tools and resources."""

import json
import pytest
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, AsyncMock

from server import (
    save_memory_tool,
    load_memory_tool,
    get_time_tool,
    calculate_tool,
    get_weather_tool,
    read_resource,
    list_tools,
    list_resources,
    load_memory,
    save_memory,
    MEMORY_FILE,
)


@pytest.fixture(autouse=True)
def cleanup_memory():
    """Clean up memory.json before and after each test."""
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()
    yield
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()


# ============================================================================
# TOOL TESTS
# ============================================================================

class TestSaveMemoryTool:
    """Test the save_memory tool."""

    @pytest.mark.asyncio
    async def test_save_single_key(self):
        """Save a single key-value pair."""
        result = await save_memory_tool({"key": "test_key", "value": "test_value"})
        assert result == "Saved test_key"
        assert load_memory() == {"test_key": "test_value"}

    @pytest.mark.asyncio
    async def test_save_multiple_keys(self):
        """Save multiple key-value pairs."""
        await save_memory_tool({"key": "key1", "value": "value1"})
        await save_memory_tool({"key": "key2", "value": "value2"})
        mem = load_memory()
        assert mem == {"key1": "value1", "key2": "value2"}

    @pytest.mark.asyncio
    async def test_overwrite_existing_key(self):
        """Overwrite an existing key."""
        await save_memory_tool({"key": "name", "value": "Alice"})
        result = await save_memory_tool({"key": "name", "value": "Bob"})
        assert result == "Saved name"
        assert load_memory() == {"name": "Bob"}


class TestLoadMemoryTool:
    """Test the load_memory tool."""

    @pytest.mark.asyncio
    async def test_load_empty_memory(self):
        """Load from empty memory file."""
        result = await load_memory_tool({})
        assert result == "{}"

    @pytest.mark.asyncio
    async def test_load_existing_memory(self):
        """Load existing memory data."""
        save_memory({"key1": "value1", "key2": "value2"})
        result = await load_memory_tool({})
        data = json.loads(result)
        assert data == {"key1": "value1", "key2": "value2"}


class TestGetTimeTool:
    """Test the get_time tool."""

    @pytest.mark.asyncio
    async def test_get_time_format(self):
        """Check that get_time returns valid ISO format."""
        result = await get_time_tool({})
        # Should be parseable as ISO format datetime
        parsed = datetime.fromisoformat(result)
        assert isinstance(parsed, datetime)

    @pytest.mark.asyncio
    async def test_get_time_roughly_current(self):
        """Check that returned time is roughly current."""
        before = datetime.now()
        result = await get_time_tool({})
        after = datetime.now()
        parsed = datetime.fromisoformat(result)
        assert before <= parsed <= after


class TestCalculateTool:
    """Test the calculate tool."""

    @pytest.mark.asyncio
    async def test_add(self):
        """Test addition."""
        result = await calculate_tool({"a": 10, "b": 5, "operation": "add"})
        assert "10" in result and "add" in result and "15" in result

    @pytest.mark.asyncio
    async def test_subtract(self):
        """Test subtraction."""
        result = await calculate_tool({"a": 10, "b": 3, "operation": "subtract"})
        assert "10" in result and "subtract" in result and "7" in result

    @pytest.mark.asyncio
    async def test_multiply(self):
        """Test multiplication."""
        result = await calculate_tool({"a": 6, "b": 7, "operation": "multiply"})
        assert "6" in result and "multiply" in result and "42" in result

    @pytest.mark.asyncio
    async def test_divide(self):
        """Test division."""
        result = await calculate_tool({"a": 20, "b": 4, "operation": "divide"})
        assert "20" in result and "divide" in result and "5" in result

    @pytest.mark.asyncio
    async def test_divide_with_floats(self):
        """Test division with decimal result."""
        result = await calculate_tool({"a": 10, "b": 3, "operation": "divide"})
        assert "10" in result and "divide" in result
        # Should contain approximately 3.333...
        assert "3.333" in result or "3.33" in result


class TestGetWeatherTool:
    """Test the get_weather tool."""

    @pytest.mark.asyncio
    async def test_get_weather_invalid_city(self):
        """Test weather for non-existent city."""
        result = await get_weather_tool({"city": "InvalidCityXYZ123"})
        assert "Could not find" in result or "unreachable" in result

    @pytest.mark.asyncio
    async def test_get_weather_real_city(self):
        """Test weather fetch for a real city (requires network)."""
        # This test hits the real wttr.in API to verify format
        result = await get_weather_tool({"city": "London"})
        # Should not have error messages
        assert "Could not find" not in result
        assert "unreachable" not in result
        # Should contain weather data
        assert "London" in result or "," in result  # City name or location format


# ============================================================================
# RESOURCE TESTS
# ============================================================================

class TestListResources:
    """Test resource advertisement."""

    @pytest.mark.asyncio
    async def test_list_resources_count(self):
        """Check that correct number of resources are advertised."""
        resources = await list_resources()
        assert len(resources) == 3

    @pytest.mark.asyncio
    async def test_list_resources_uris(self):
        """Check that all expected resource URIs are present."""
        resources = await list_resources()
        uris = [r["uri"] for r in resources]
        assert "memory://data" in uris
        assert "file://memory.json" in uris
        assert "status://server" in uris

    @pytest.mark.asyncio
    async def test_list_resources_have_descriptions(self):
        """Check that all resources have descriptions."""
        resources = await list_resources()
        for resource in resources:
            assert "description" in resource
            assert len(resource["description"]) > 0


class TestReadResource:
    """Test reading resources."""

    @pytest.mark.asyncio
    async def test_read_memory_data_empty(self):
        """Read memory://data when empty."""
        result = await read_resource("memory://data")
        assert result == "{}"

    @pytest.mark.asyncio
    async def test_read_memory_data_with_content(self):
        """Read memory://data with existing content."""
        save_memory({"key1": "value1", "key2": "value2"})
        result = await read_resource("memory://data")
        data = json.loads(result)
        assert data == {"key1": "value1", "key2": "value2"}

    @pytest.mark.asyncio
    async def test_read_file_memory_json(self):
        """Read file://memory.json resource."""
        save_memory({"project": "MCP"})
        result = await read_resource("file://memory.json")
        data = json.loads(result)
        assert data == {"project": "MCP"}

    @pytest.mark.asyncio
    async def test_read_file_memory_json_with_trailing_slash(self):
        """Read file://memory.json/ (with trailing slash)."""
        save_memory({"test": "data"})
        result = await read_resource("file://memory.json/")
        data = json.loads(result)
        assert data == {"test": "data"}

    @pytest.mark.asyncio
    async def test_read_status_server(self):
        """Read status://server resource."""
        save_memory({"entry1": "value1"})
        result = await read_resource("status://server")
        assert "MCP Server Status" in result
        assert "simple-mcp-server" in result
        assert "Running" in result
        assert "Entries: 1" in result

    @pytest.mark.asyncio
    async def test_read_status_server_empty_memory(self):
        """Read status://server with no memory entries."""
        result = await read_resource("status://server")
        assert "Entries: 0" in result
        assert "none" in result

    @pytest.mark.asyncio
    async def test_read_unknown_resource(self):
        """Read non-existent resource."""
        result = await read_resource("unknown://resource")
        assert "Unknown resource" in result


# ============================================================================
# TOOL ADVERTISEMENT TESTS
# ============================================================================

class TestListTools:
    """Test tool advertisement."""

    @pytest.mark.asyncio
    async def test_list_tools_count(self):
        """Check that correct number of tools are advertised."""
        tools = await list_tools()
        assert len(tools) == 5

    @pytest.mark.asyncio
    async def test_list_tools_names(self):
        """Check that all expected tools are present."""
        tools = await list_tools()
        names = [t["name"] for t in tools]
        assert "save_memory" in names
        assert "load_memory" in names
        assert "get_time" in names
        assert "calculate" in names
        assert "get_weather" in names

    @pytest.mark.asyncio
    async def test_tools_have_descriptions(self):
        """Check that all tools have descriptions."""
        tools = await list_tools()
        for tool in tools:
            assert "description" in tool
            assert len(tool["description"]) > 0

    @pytest.mark.asyncio
    async def test_tools_have_input_schema(self):
        """Check that all tools have input schemas."""
        tools = await list_tools()
        for tool in tools:
            assert "inputSchema" in tool
            assert "type" in tool["inputSchema"]

    @pytest.mark.asyncio
    async def test_calculate_tool_schema_operations(self):
        """Check that calculate tool lists valid operations."""
        tools = await list_tools()
        calc_tool = next(t for t in tools if t["name"] == "calculate")
        operations = calc_tool["inputSchema"]["properties"]["operation"]["enum"]
        assert set(operations) == {"add", "subtract", "multiply", "divide"}


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple tools/resources."""

    @pytest.mark.asyncio
    async def test_save_then_load_workflow(self):
        """Save data with tool, then read with resource."""
        await save_memory_tool({"key": "workflow_test", "value": "integration"})
        resource_data = await read_resource("memory://data")
        data = json.loads(resource_data)
        assert data["workflow_test"] == "integration"

    @pytest.mark.asyncio
    async def test_status_reflects_memory_changes(self):
        """Status resource should show current memory count."""
        await save_memory_tool({"key": "item1", "value": "val1"})
        status = await read_resource("status://server")
        assert "Entries: 1" in status

        await save_memory_tool({"key": "item2", "value": "val2"})
        status = await read_resource("status://server")
        assert "Entries: 2" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
