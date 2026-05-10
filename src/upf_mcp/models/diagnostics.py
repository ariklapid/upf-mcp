"""Diagnostic and source-location models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DiagnosticSeverity(str, Enum):
    """Severity levels for user-facing parser and validation diagnostics."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SourceLocation(BaseModel):
    """One-based source span for a parsed object or diagnostic."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(description="Project-relative or display path for the source file.")
    line: int = Field(description="One-based starting line.", ge=1)
    column: int = Field(description="One-based starting column.", ge=1)
    end_line: int | None = Field(default=None, description="One-based ending line when known.", ge=1)
    end_column: int | None = Field(
        default=None,
        description="One-based ending column when known.",
        ge=1,
    )


class Diagnostic(BaseModel):
    """Source-location-aware diagnostic returned by parser and rule stages."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(description="Stable diagnostic code.")
    severity: DiagnosticSeverity = Field(description="Diagnostic severity.")
    message: str = Field(description="Concise human-readable diagnostic message.")
    location: SourceLocation | None = Field(
        default=None,
        description="Source location for the diagnostic when available.",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Compact evidence strings supporting the diagnostic.",
    )
    suggested_fix: str | None = Field(
        default=None,
        description="Actionable fix or next step when known.",
    )
