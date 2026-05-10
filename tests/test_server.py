from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from mcp.types import TextContent

from upf_mcp import __version__
from upf_mcp.server import (
    PUBLIC_TOOL_NAMES,
    SERVER_NAME,
    build_ping_result,
    create_server,
    parse_upf_file,
)

FIXTURES = Path(__file__).parent / "fixtures"


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
        assert set(tool_map) == {PUBLIC_TOOL_NAMES["ping"], PUBLIC_TOOL_NAMES["parse_upf"]}
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


def test_parse_upf_file_reads_file_under_project_root() -> None:
    result = parse_upf_file(
        str(FIXTURES),
        "upf/supported.upf",
    )

    assert result.status == "ok"
    assert result.command_count == 3
    assert result.power_domain_count == 2
    assert result.unsupported_command_count == 0
    assert result.document is not None
    assert result.document.power_domains[1].elements == ["u_core", "u_mem"]


def test_parse_upf_file_rejects_path_outside_project_root() -> None:
    with TemporaryDirectory() as project_root, TemporaryDirectory() as outside_root:
        outside = Path(outside_root) / "outside.upf"
        outside.write_text("set_scope /top\n", encoding="utf-8")

        result = parse_upf_file(project_root, str(outside))

    assert result.status == "error"
    assert result.document is None
    assert result.diagnostics[0].code == "path_outside_root"


def test_upf_parse_upf_tool_returns_structured_parse_result() -> None:
    server = create_server()

    async def run() -> dict[str, Any]:
        _content, structured = await server.call_tool(
            PUBLIC_TOOL_NAMES["parse_upf"],
            {
                "project_root": str(FIXTURES),
                "path": "upf/unsupported.upf",
                "max_diagnostics": 1,
            },
        )
        return cast(dict[str, Any], structured)

    structured = asyncio.run(run())

    assert structured["status"] == "ok"
    assert structured["command_count"] == 4
    assert structured["unsupported_command_count"] == 1
    assert structured["diagnostics_truncated"] is True
    assert [diagnostic["code"] for diagnostic in structured["diagnostics"]] == [
        "unsupported_command"
    ]
