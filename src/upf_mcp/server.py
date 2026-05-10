"""FastMCP server wiring for upf-mcp."""

from __future__ import annotations

import platform

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from . import __version__

SERVER_NAME = "upf_mcp"
TOOL_NAME_PREFIX = "upf_"
PUBLIC_TOOL_NAMES = {
    "ping": f"{TOOL_NAME_PREFIX}ping",
}

READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


class PingResult(BaseModel):
    """Health and version metadata returned by `upf_ping`."""

    status: str = Field(description="Server health status.")
    server_name: str = Field(description="Canonical MCP server name.")
    version: str = Field(description="Installed upf-mcp package version.")
    python_version: str = Field(description="Python runtime version.")


def build_ping_result() -> PingResult:
    """Build the static health payload for `upf_ping`."""

    return PingResult(
        status="ok",
        server_name=SERVER_NAME,
        version=__version__,
        python_version=platform.python_version(),
    )


def create_server() -> FastMCP:
    """Create the MCP server instance."""

    mcp = FastMCP(SERVER_NAME)

    @mcp.tool(
        name=PUBLIC_TOOL_NAMES["ping"],
        annotations=READ_ONLY_ANNOTATIONS,
    )
    async def upf_ping() -> PingResult:
        """Return UPF MCP server health and version metadata.

        Returns:
            PingResult: Structured health metadata with this schema:
            {
              "status": "ok",
              "server_name": "upf_mcp",
              "version": "<package version>",
              "python_version": "<runtime version>"
            }
        """

        return build_ping_result()

    return mcp
