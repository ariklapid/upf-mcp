"""Small non-executing Tcl/UPF parser for the first command subset."""

from __future__ import annotations

from dataclasses import dataclass

from upf_mcp.models import (
    Diagnostic,
    DiagnosticSeverity,
    PowerDomain,
    SetScope,
    SourceLocation,
    UnsupportedCommand,
    UPFCommand,
    UPFDocument,
)

SUPPORTED_COMMANDS = frozenset({"set_scope", "create_power_domain"})


@dataclass(frozen=True)
class _CommandText:
    raw: str
    location: SourceLocation


def parse_upf_text(text: str, *, path: str) -> UPFDocument:
    """Parse UPF text into the MVP document IR.

    The parser treats UPF as Tcl command structure only. It does not evaluate
    variables, command substitutions, sourced files, procedures, or expressions.
    """

    diagnostics: list[Diagnostic] = []
    commands: list[UPFCommand] = []
    scopes: list[SetScope] = []
    power_domains: list[PowerDomain] = []
    unsupported_commands: list[UnsupportedCommand] = []
    current_scope: str | None = None

    for command_text in _split_commands(text, path=path):
        tokens, token_diagnostics = _tokenize_command(command_text)
        diagnostics.extend(token_diagnostics)
        if not tokens:
            continue

        command_name = tokens[0]
        arguments = tokens[1:]
        command = UPFCommand(
            command=command_name,
            arguments=arguments,
            location=command_text.location,
            raw=command_text.raw,
        )
        commands.append(command)

        if command_name == "set_scope":
            parsed_scope = _collect_set_scope(arguments, command_text.location, diagnostics)
            if parsed_scope is not None:
                current_scope = parsed_scope.scope
                scopes.append(parsed_scope)
        elif command_name == "create_power_domain":
            domain = _collect_power_domain(
                arguments,
                current_scope=current_scope,
                location=command_text.location,
                diagnostics=diagnostics,
            )
            if domain is not None:
                power_domains.append(domain)
        else:
            unsupported_commands.append(
                UnsupportedCommand(
                    command=command_name,
                    arguments=arguments,
                    location=command_text.location,
                    raw=command_text.raw,
                )
            )
            diagnostics.append(
                Diagnostic(
                    code="unsupported_command",
                    severity=DiagnosticSeverity.WARNING,
                    message=f"Unsupported UPF command `{command_name}`.",
                    location=command_text.location,
                    evidence=[command_text.raw],
                    suggested_fix=(
                        "Use a supported command subset or expect this command to be "
                        "ignored by semantic collection."
                    ),
                )
            )

    return UPFDocument(
        path=path,
        commands=commands,
        scopes=scopes,
        power_domains=power_domains,
        unsupported_commands=unsupported_commands,
        diagnostics=diagnostics,
    )


def _split_commands(text: str, *, path: str) -> list[_CommandText]:
    commands: list[_CommandText] = []
    buffer: list[str] = []
    command_start: tuple[int, int] | None = None
    last_char_location: tuple[int, int] | None = None
    brace_depth = 0
    in_quote = False
    escaped = False
    line = 1
    column = 1
    index = 0

    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if char == "\\" and next_char == "\n":
            if command_start is not None:
                buffer.append(" ")
            index += 2
            line += 1
            column = 1
            escaped = False
            continue

        if command_start is None:
            if char in " \t\r":
                index += 1
                column += 1
                continue
            if char == "\n":
                index += 1
                line += 1
                column = 1
                continue
            if char == "#":
                index, line, column = _skip_comment(text, index, line, column)
                continue
            command_start = (line, column)

        if escaped:
            buffer.append(char)
            last_char_location = (line, column)
            escaped = False
        elif char == "\\":
            buffer.append(char)
            last_char_location = (line, column)
            escaped = True
        elif char == '"' and brace_depth == 0:
            buffer.append(char)
            last_char_location = (line, column)
            in_quote = not in_quote
        elif char == "{" and not in_quote:
            buffer.append(char)
            last_char_location = (line, column)
            brace_depth += 1
        elif char == "}" and not in_quote:
            buffer.append(char)
            last_char_location = (line, column)
            brace_depth = max(0, brace_depth - 1)
        elif char in "\n;" and brace_depth == 0 and not in_quote:
            _append_command(
                commands,
                buffer,
                path=path,
                command_start=command_start,
                last_char_location=last_char_location,
            )
            buffer = []
            command_start = None
            last_char_location = None
            escaped = False
        else:
            buffer.append(char)
            if char not in " \t\r":
                last_char_location = (line, column)

        if char == "\n":
            line += 1
            column = 1
        else:
            column += 1
        index += 1

    _append_command(
        commands,
        buffer,
        path=path,
        command_start=command_start,
        last_char_location=last_char_location,
    )
    return commands


def _skip_comment(text: str, index: int, line: int, column: int) -> tuple[int, int, int]:
    while index < len(text) and text[index] != "\n":
        index += 1
        column += 1
    return index, line, column


def _append_command(
    commands: list[_CommandText],
    buffer: list[str],
    *,
    path: str,
    command_start: tuple[int, int] | None,
    last_char_location: tuple[int, int] | None,
) -> None:
    raw = "".join(buffer).strip()
    if not raw or command_start is None:
        return
    end_line, end_column = last_char_location or command_start
    commands.append(
        _CommandText(
            raw=raw,
            location=SourceLocation(
                path=path,
                line=command_start[0],
                column=command_start[1],
                end_line=end_line,
                end_column=end_column,
            ),
        )
    )


def _tokenize_command(command: _CommandText) -> tuple[list[str], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    tokens: list[str] = []
    token: list[str] = []
    in_quote = False
    index = 0

    while index < len(command.raw):
        char = command.raw[index]
        if char.isspace() and not in_quote:
            _append_token(tokens, token)
        elif char == "\\":
            if index + 1 < len(command.raw):
                token.append(command.raw[index + 1])
                index += 1
            else:
                token.append(char)
        elif char == '"' and not in_quote and not token:
            in_quote = True
        elif char == '"' and in_quote:
            in_quote = False
        elif char == "{" and not in_quote and not token:
            grouped, next_index, ok = _read_braced_token(command.raw, index)
            token.append(grouped)
            index = next_index
            if not ok:
                diagnostics.append(
                    Diagnostic(
                        code="unterminated_brace",
                        severity=DiagnosticSeverity.ERROR,
                        message="Unterminated braced Tcl token.",
                        location=command.location,
                        evidence=[command.raw],
                        suggested_fix=(
                            "Close the braced list or expression before the command ends."
                        ),
                    )
                )
        else:
            token.append(char)
        index += 1

    _append_token(tokens, token)
    if in_quote:
        diagnostics.append(
            Diagnostic(
                code="unterminated_quote",
                severity=DiagnosticSeverity.ERROR,
                message="Unterminated quoted Tcl token.",
                location=command.location,
                evidence=[command.raw],
                suggested_fix="Close the quoted token before the command ends.",
            )
        )
    return tokens, diagnostics


def _append_token(tokens: list[str], token: list[str]) -> None:
    if token:
        tokens.append("".join(token))
        token.clear()


def _read_braced_token(raw: str, index: int) -> tuple[str, int, bool]:
    depth = 1
    token: list[str] = []
    index += 1
    while index < len(raw):
        char = raw[index]
        if char == "{":
            depth += 1
            token.append(char)
        elif char == "}":
            depth -= 1
            if depth == 0:
                return "".join(token), index, True
            token.append(char)
        else:
            token.append(char)
        index += 1
    return "".join(token), index - 1, False


def _collect_set_scope(
    arguments: list[str],
    location: SourceLocation,
    diagnostics: list[Diagnostic],
) -> SetScope | None:
    if not arguments:
        diagnostics.append(
            Diagnostic(
                code="missing_set_scope_argument",
                severity=DiagnosticSeverity.ERROR,
                message="`set_scope` requires a scope path argument.",
                location=location,
                suggested_fix="Pass the hierarchy scope, for example `set_scope /top`.",
            )
        )
        return None
    if len(arguments) > 1:
        diagnostics.append(
            Diagnostic(
                code="extra_set_scope_arguments",
                severity=DiagnosticSeverity.WARNING,
                message="`set_scope` MVP handling uses only the first argument.",
                location=location,
                evidence=arguments[1:],
                suggested_fix="Keep `set_scope` to a single scope path for MVP parsing.",
            )
        )
    return SetScope(scope=arguments[0], location=location)


def _collect_power_domain(
    arguments: list[str],
    *,
    current_scope: str | None,
    location: SourceLocation,
    diagnostics: list[Diagnostic],
) -> PowerDomain | None:
    if not arguments:
        diagnostics.append(
            Diagnostic(
                code="missing_power_domain_name",
                severity=DiagnosticSeverity.ERROR,
                message="`create_power_domain` requires a domain name.",
                location=location,
                suggested_fix="Pass a domain name after `create_power_domain`.",
            )
        )
        return None

    name = arguments[0]
    elements: list[str] = []
    include_scope = False
    raw_options: dict[str, list[str]] = {}
    index = 1

    while index < len(arguments):
        argument = arguments[index]
        if argument == "-elements":
            if index + 1 >= len(arguments):
                diagnostics.append(
                    Diagnostic(
                        code="missing_power_domain_elements",
                        severity=DiagnosticSeverity.ERROR,
                        message="`create_power_domain -elements` requires a Tcl list argument.",
                        location=location,
                        suggested_fix="Add an elements list, for example `-elements {u_block}`.",
                    )
                )
                break
            elements.extend(_split_tcl_list(arguments[index + 1]))
            index += 2
        elif argument == "-include_scope":
            include_scope = True
            index += 1
        elif argument.startswith("-"):
            values: list[str] = []
            if index + 1 < len(arguments) and not arguments[index + 1].startswith("-"):
                values.append(arguments[index + 1])
                index += 1
            raw_options.setdefault(argument, []).extend(values)
            diagnostics.append(
                Diagnostic(
                    code="unsupported_power_domain_option",
                    severity=DiagnosticSeverity.WARNING,
                    message=f"Unsupported `create_power_domain` option `{argument}`.",
                    location=location,
                    evidence=[argument, *values],
                    suggested_fix="Expect this option to be preserved only as raw parser data.",
                )
            )
            index += 1
        else:
            raw_options.setdefault("__positional__", []).append(argument)
            diagnostics.append(
                Diagnostic(
                    code="unexpected_power_domain_argument",
                    severity=DiagnosticSeverity.WARNING,
                    message=f"Unexpected `create_power_domain` argument `{argument}`.",
                    location=location,
                    evidence=[argument],
                    suggested_fix="Use supported options such as `-elements` or `-include_scope`.",
                )
            )
            index += 1

    return PowerDomain(
        name=name,
        scope=current_scope,
        elements=elements,
        include_scope=include_scope,
        raw_options=raw_options,
        location=location,
    )


def _split_tcl_list(value: str) -> list[str]:
    nested_command = _CommandText(
        raw=value,
        location=SourceLocation(path="<list>", line=1, column=1),
    )
    tokens, _ = _tokenize_command(nested_command)
    return tokens
