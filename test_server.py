#!/usr/bin/env python3
"""Test suite for the FastMCP server: tools, resources, and prompts."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx2
import pytest

import server
from server import mcp
from mcp.server.mcpserver.exceptions import ToolError
from resources import memory_store


@pytest.fixture(autouse=True)
def tmp_memory(tmp_path, monkeypatch):
    """Point the memory store at a temp file so tests never touch the real memory.json."""
    monkeypatch.setattr(memory_store, "MEMORY_FILE", tmp_path / "memory.json")


async def call(name, **args):
    result = await mcp.call_tool(name, args)
    return result.content[0].text, result.is_error


async def read(uri):
    return list(await mcp.read_resource(uri))[0].content


async def prompt_text(name, **args):
    result = await mcp.get_prompt(name, args)
    return result.messages[0].content.text


# ============================================================================
# TOOLS
# ============================================================================
class TestMemoryTools:
    async def test_save_and_load(self):
        text, err = await call("save_memory", key="k", value="v")
        assert text == "Saved k" and not err
        text, _ = await call("load_memory")
        assert json.loads(text) == {"k": "v"}

    async def test_save_overwrites_and_accumulates(self):
        await call("save_memory", key="a", value="1")
        await call("save_memory", key="b", value="2")
        await call("save_memory", key="a", value="3")
        text, _ = await call("load_memory")
        assert json.loads(text) == {"a": "3", "b": "2"}

    async def test_load_empty(self):
        text, _ = await call("load_memory")
        assert json.loads(text) == {}

    async def test_missing_argument_raises(self):
        with pytest.raises(ToolError):
            await call("save_memory", key="only_key")


class TestGetTime:
    async def test_returns_iso_timestamp(self):
        from datetime import datetime

        text, err = await call("get_time")
        assert not err
        datetime.fromisoformat(text)


class TestCalculate:
    @pytest.mark.parametrize(
        "op,expected",
        [("add", 14.0), ("subtract", 6.0), ("multiply", 40.0), ("divide", 2.5)],
    )
    async def test_operations(self, op, expected):
        text, err = await call("calculate", a=10, b=4, operation=op)
        assert not err
        assert text == f"10.0 {op} 4.0 = {expected}"

    async def test_divide_by_zero(self):
        text, err = await call("calculate", a=1, b=0, operation="divide")
        assert text == "Cannot divide by zero." and not err

    async def test_invalid_operation_rejected(self):
        with pytest.raises(ToolError):
            await call("calculate", a=1, b=2, operation="power")


WEATHER_JSON = {
    "current_condition": [
        {
            "weatherDesc": [{"value": "Sunny "}],
            "temp_C": "21",
            "FeelsLikeC": "20",
            "humidity": "40",
            "windspeedKmph": "10",
        }
    ],
    "nearest_area": [{"areaName": [{"value": "London"}], "country": [{"value": "UK"}]}],
}


def mock_client(get_side_effect=None, response=None):
    client = MagicMock()
    client.get = AsyncMock(side_effect=get_side_effect, return_value=response)
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=client)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


class TestGetWeather:
    async def test_success(self):
        resp = MagicMock()
        resp.json.return_value = WEATHER_JSON
        with patch.object(server.httpx2, "AsyncClient", return_value=mock_client(response=resp)):
            text, err = await call("get_weather", city="London")
        assert not err
        assert text == "London, UK: Sunny, 21C (feels like 20C), humidity 40%, wind 10 km/h"

    async def test_unknown_city(self):
        resp = MagicMock()
        resp.raise_for_status.side_effect = httpx2.HTTPStatusError("404", request=MagicMock(), response=MagicMock())
        with patch.object(server.httpx2, "AsyncClient", return_value=mock_client(response=resp)):
            text, _ = await call("get_weather", city="Nowhere")
        assert text == "Could not find weather for 'Nowhere'."

    async def test_service_unreachable(self):
        err = httpx2.ConnectError("boom")
        with patch.object(server.httpx2, "AsyncClient", return_value=mock_client(get_side_effect=err)):
            text, _ = await call("get_weather", city="London")
        assert text.startswith("Weather service unreachable")


class TestListTools:
    async def test_tool_names_and_schemas(self):
        tools = {t.name: t for t in await mcp.list_tools()}
        assert set(tools) == {"save_memory", "load_memory", "get_time", "calculate", "get_weather"}
        assert tools["save_memory"].input_schema["required"] == ["key", "value"]
        assert tools["calculate"].input_schema["properties"]["operation"]["enum"] == [
            "add", "subtract", "multiply", "divide",
        ]
        assert all(t.description for t in tools.values())


# ============================================================================
# RESOURCES
# ============================================================================
class TestResources:
    async def test_list(self):
        uris = {str(r.uri) for r in await mcp.list_resources()}
        assert uris == {"memory://data", "file://memory.json", "status://server"}

    @pytest.mark.parametrize("uri", ["memory://data", "file://memory.json"])
    async def test_memory_resources_match_saved_data(self, uri):
        await call("save_memory", key="k", value="v")
        assert json.loads(await read(uri)) == {"k": "v"}

    async def test_status_reports_memory(self):
        await call("save_memory", key="alpha", value="1")
        status = await read("status://server")
        assert "Server: simple-mcp-server" in status
        assert "Entries: 1" in status and "alpha" in status

    async def test_unknown_resource_raises(self):
        with pytest.raises(Exception):
            await read("nope://missing")


# ============================================================================
# PROMPTS
# ============================================================================
class TestPrompts:
    async def test_list(self):
        prompts = {p.name: p for p in await mcp.list_prompts()}
        assert set(prompts) == {"weather_activity_planner", "weather_alert_explainer"}
        args = {a.name: a.required for a in prompts["weather_activity_planner"].arguments}
        assert args == {"location": True, "activity_type": True, "time_horizon": False}

    async def test_activity_planner(self):
        text = await prompt_text(
            "weather_activity_planner", location="Colorado", activity_type="hiking", time_horizon="this weekend"
        )
        assert "hiking in Colorado this weekend" in text

    async def test_activity_planner_default_horizon(self):
        text = await prompt_text("weather_activity_planner", location="Oslo", activity_type="run")
        assert "run in Oslo soon" in text

    async def test_alert_explainer(self):
        text = await prompt_text("weather_alert_explainer", alert_type="heat advisory", region="Texas")
        assert "heat advisory alert for Texas" in text

    async def test_missing_required_argument_raises(self):
        with pytest.raises(Exception):
            await prompt_text("weather_alert_explainer", alert_type="x")
