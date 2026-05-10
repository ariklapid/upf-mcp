from __future__ import annotations

import asyncio
from typing import Any, cast

from mcp.types import TextContent

from upf_mcp import __version__
from upf_mcp.server import PUBLIC_TOOL_NAMES, SERVER_NAME, build_ping_result, create_server


def test_build_ping_result() -> None:
    payload = build_ping_result()

    assert payload.status == "ok"
    assert payload.server_name == SERVER_NAME
    assert payload.version == __version__
    assert payload.python_version


def test_tools_list_exposes_ping_schema_and_annotations() -> None:
    server = create_server()

    async def run() -> dict[str, Any]:
        tools = await server.list_tools()
        tool_map = {tool.name: tool for tool in tools}
        assert set(tool_map) == {PUBLIC_TOOL_NAMES["ping"]}
        return cast(dict[str, Any], tool_map[PUBLIC_TOOL_NAMES["ping"]].model_dump())

    tool = asyncio.run(run())

    assert tool["inputSchema"]["properties"] == {}
    assert tool["outputSchema"]["title"] == "PingResult"
    assert tool["annotations"]["readOnlyHint"] is True
    assert tool["annotations"]["destructiveHint"] is False
    assert tool["annotations"]["idempotentHint"] is True
    assert tool["annotations"]["openWorldHint"] is False


def test_upf_ping_tool_returns_structured_health_payload() -> None:
    server = create_server()

    async def run() -> tuple[list[Any], dict[str, str]]:
        content, structured = await server.call_tool(PUBLIC_TOOL_NAMES["ping"], {})
        return cast(list[Any], content), cast(dict[str, str], structured)

    content, structured = asyncio.run(run())

    assert structured["status"] == "ok"
    assert structured["server_name"] == SERVER_NAME
    assert structured["version"] == __version__
    assert content
    assert isinstance(content[0], TextContent)
    assert '"status": "ok"' in content[0].text
