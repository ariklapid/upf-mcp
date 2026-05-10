"""UPF intermediate-representation models for the first parser slice."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .diagnostics import Diagnostic, SourceLocation


class UPFCommand(BaseModel):
    """Shallow representation of one Tcl/UPF command."""

    model_config = ConfigDict(extra="forbid")

    command: str = Field(description="Command name.")
    arguments: list[str] = Field(default_factory=list, description="Tokenized command arguments.")
    location: SourceLocation = Field(description="Source location for the command.")
    raw: str = Field(description="Original command text after line-continuation joining.")


class SetScope(BaseModel):
    """Typed IR for `set_scope`."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["set_scope"] = "set_scope"
    scope: str = Field(description="Scope path argument.")
    location: SourceLocation = Field(description="Source location for the command.")


class PowerDomain(BaseModel):
    """Typed IR for `create_power_domain`."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["create_power_domain"] = "create_power_domain"
    name: str = Field(description="Power-domain name.")
    scope: str | None = Field(
        default=None,
        description="Current UPF scope when the domain command was parsed.",
    )
    elements: list[str] = Field(
        default_factory=list,
        description="Element paths captured from `-elements` when present.",
    )
    include_scope: bool = Field(
        default=False,
        description="Whether `-include_scope` was present.",
    )
    raw_options: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Option tokens preserved for unsupported or future handling.",
    )
    location: SourceLocation = Field(description="Source location for the command.")


class UnsupportedCommand(BaseModel):
    """Command that was parsed as Tcl but is not semantically supported yet."""

    model_config = ConfigDict(extra="forbid")

    command: str = Field(description="Unsupported command name.")
    arguments: list[str] = Field(default_factory=list, description="Tokenized command arguments.")
    location: SourceLocation = Field(description="Source location for the command.")
    raw: str = Field(description="Original command text after line-continuation joining.")


class UPFDocument(BaseModel):
    """Parsed UPF document for the MVP parser path."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(description="Project-relative or display path for the UPF file.")
    commands: list[UPFCommand] = Field(
        default_factory=list,
        description="All parsed Tcl/UPF commands.",
    )
    scopes: list[SetScope] = Field(default_factory=list, description="Parsed `set_scope` commands.")
    power_domains: list[PowerDomain] = Field(
        default_factory=list,
        description="Parsed `create_power_domain` commands.",
    )
    unsupported_commands: list[UnsupportedCommand] = Field(
        default_factory=list,
        description="Commands not supported by this parser stage.",
    )
    diagnostics: list[Diagnostic] = Field(
        default_factory=list,
        description="Parser and collection diagnostics.",
    )


class ParseUPFFileResult(BaseModel):
    """Result returned by the `upf_parse_upf` MCP tool."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "error"] = Field(description="Tool execution status.")
    project_root: str = Field(description="Resolved project root.")
    path: str = Field(description="Project-relative UPF file path.")
    document: UPFDocument | None = Field(
        default=None,
        description="Parsed UPF document when file loading and parsing succeeded.",
    )
    command_count: int = Field(default=0, description="Number of parsed commands.", ge=0)
    power_domain_count: int = Field(default=0, description="Number of parsed domains.", ge=0)
    unsupported_command_count: int = Field(
        default=0,
        description="Number of parsed commands outside the supported subset.",
        ge=0,
    )
    diagnostics: list[Diagnostic] = Field(
        default_factory=list,
        description="Bounded diagnostics for the tool result.",
    )
    diagnostics_truncated: bool = Field(
        default=False,
        description="Whether diagnostics were truncated by the requested limit.",
    )
