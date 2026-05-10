"""FastMCP server wiring for upf-mcp."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from . import __version__
from .models import Diagnostic, DiagnosticSeverity, ParseUPFFileResult
from .upf import parse_upf_text

SERVER_NAME = "upf_mcp"
TOOL_NAME_PREFIX = "upf_"
PUBLIC_TOOL_NAMES = {
    "ping": f"{TOOL_NAME_PREFIX}ping",
    "parse_upf": f"{TOOL_NAME_PREFIX}parse_upf",
}
MAX_PARSE_DIAGNOSTICS = 1000

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


ProjectRootArg = Annotated[
    str,
    Field(
        description=("Declared project root. The UPF path must resolve inside this directory."),
    ),
]
UPFPathArg = Annotated[
    str,
    Field(
        description=("Project-relative or absolute UPF file path under `project_root`."),
    ),
]
MaxDiagnosticsArg = Annotated[
    int,
    Field(
        description="Maximum diagnostics to include in the tool result.",
        ge=0,
        le=MAX_PARSE_DIAGNOSTICS,
    ),
]


def build_ping_result() -> PingResult:
    """Build the static health payload for `upf_ping`."""

    return PingResult(
        status="ok",
        server_name=SERVER_NAME,
        version=__version__,
        python_version=platform.python_version(),
    )


def parse_upf_file(
    project_root: str, path: str, *, max_diagnostics: int = 100
) -> ParseUPFFileResult:
    """Load and parse a UPF file under a declared project root."""

    root, upf_path, relative_path, diagnostics = _resolve_upf_path(project_root, path)
    if diagnostics:
        return ParseUPFFileResult(
            status="error",
            project_root=str(root) if root is not None else project_root,
            path=path,
            diagnostics=_limit_diagnostics(diagnostics, max_diagnostics),
            diagnostics_truncated=len(diagnostics) > max_diagnostics,
        )

    assert root is not None
    assert upf_path is not None
    assert relative_path is not None

    try:
        text = upf_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        diagnostics = [
            Diagnostic(
                code="file_decode_error",
                severity=DiagnosticSeverity.ERROR,
                message="Could not read UPF file as UTF-8 text.",
                suggested_fix="Check that the UPF file is text encoded as UTF-8.",
            )
        ]
        return ParseUPFFileResult(
            status="error",
            project_root=str(root),
            path=relative_path,
            diagnostics=diagnostics,
        )
    except OSError as exc:
        diagnostics = [
            Diagnostic(
                code="file_read_error",
                severity=DiagnosticSeverity.ERROR,
                message=f"Could not read UPF file: {type(exc).__name__}.",
                suggested_fix="Verify that the path exists, is readable, and is not a directory.",
            )
        ]
        return ParseUPFFileResult(
            status="error",
            project_root=str(root),
            path=relative_path,
            diagnostics=diagnostics,
        )

    document = parse_upf_text(text, path=relative_path)
    diagnostics = document.diagnostics
    limited_diagnostics = _limit_diagnostics(diagnostics, max_diagnostics)
    if len(limited_diagnostics) != len(diagnostics):
        document = document.model_copy(update={"diagnostics": limited_diagnostics})

    return ParseUPFFileResult(
        status="ok",
        project_root=str(root),
        path=relative_path,
        document=document,
        command_count=len(document.commands),
        power_domain_count=len(document.power_domains),
        unsupported_command_count=len(document.unsupported_commands),
        diagnostics=limited_diagnostics,
        diagnostics_truncated=len(diagnostics) > max_diagnostics,
    )


def _resolve_upf_path(
    project_root: str,
    path: str,
) -> tuple[Path | None, Path | None, str | None, list[Diagnostic]]:
    try:
        root = Path(project_root).expanduser().resolve(strict=True)
    except OSError as exc:
        return (
            None,
            None,
            None,
            [
                Diagnostic(
                    code="invalid_project_root",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Could not resolve project root: {type(exc).__name__}.",
                    suggested_fix="Pass an existing readable directory as `project_root`.",
                )
            ],
        )

    if not root.is_dir():
        return (
            root,
            None,
            None,
            [
                Diagnostic(
                    code="invalid_project_root",
                    severity=DiagnosticSeverity.ERROR,
                    message="Project root is not a directory.",
                    suggested_fix="Pass an existing readable directory as `project_root`.",
                )
            ],
        )

    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        return (
            root,
            None,
            path,
            [
                Diagnostic(
                    code="file_not_found",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Could not resolve UPF file path: {type(exc).__name__}.",
                    suggested_fix="Pass an existing UPF file under `project_root`.",
                )
            ],
        )

    try:
        relative_path = resolved.relative_to(root).as_posix()
    except ValueError:
        return (
            root,
            None,
            path,
            [
                Diagnostic(
                    code="path_outside_root",
                    severity=DiagnosticSeverity.ERROR,
                    message="UPF path resolves outside the declared project root.",
                    suggested_fix="Keep every requested path under `project_root`.",
                )
            ],
        )

    if not resolved.is_file():
        return (
            root,
            None,
            relative_path,
            [
                Diagnostic(
                    code="not_a_file",
                    severity=DiagnosticSeverity.ERROR,
                    message="UPF path is not a file.",
                    suggested_fix="Pass a readable `.upf` file path.",
                )
            ],
        )

    return root, resolved, relative_path, []


def _limit_diagnostics(diagnostics: list[Diagnostic], limit: int) -> list[Diagnostic]:
    if limit <= 0:
        return []
    return diagnostics[:limit]


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

    @mcp.tool(
        name=PUBLIC_TOOL_NAMES["parse_upf"],
        annotations=READ_ONLY_ANNOTATIONS,
    )
    async def upf_parse_upf(
        project_root: ProjectRootArg,
        path: UPFPathArg,
        max_diagnostics: MaxDiagnosticsArg = 100,
    ) -> ParseUPFFileResult:
        """Parse a UPF file into the MVP IR and diagnostics.

        This tool is read-only. It validates that `path` resolves inside
        `project_root`, reads the file as UTF-8 text, parses Tcl command
        structure without executing Tcl, and semantically collects only
        `set_scope` and `create_power_domain`.

        Args:
            project_root (str): Existing directory that bounds file access.
            path (str): UPF file path under `project_root`.
            max_diagnostics (int): Maximum diagnostics to include, from 0 to 1000.

        Returns:
            ParseUPFFileResult: Structured parse result containing the document,
            command counts, unsupported-command counts, and bounded diagnostics.
        """

        return parse_upf_file(
            project_root=project_root,
            path=path,
            max_diagnostics=max_diagnostics,
        )

    return mcp
