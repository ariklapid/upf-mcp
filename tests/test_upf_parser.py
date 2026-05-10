from __future__ import annotations

from pathlib import Path

from upf_mcp.upf import parse_upf_text

FIXTURES = Path(__file__).parent / "fixtures" / "upf"


def test_parse_supported_fixture_collects_scope_and_domains() -> None:
    text = (FIXTURES / "supported.upf").read_text(encoding="utf-8")

    document = parse_upf_text(text, path="supported.upf")

    assert len(document.commands) == 3
    assert document.diagnostics == []
    assert document.scopes[0].scope == "/top"
    assert [domain.name for domain in document.power_domains] == ["PD_TOP", "PD_SW"]
    assert document.power_domains[0].include_scope is True
    assert document.power_domains[0].scope == "/top"
    assert document.power_domains[1].elements == ["u_core", "u_mem"]
    assert document.power_domains[1].location.line == 5


def test_parse_unsupported_fixture_reports_unsupported_constructs() -> None:
    text = (FIXTURES / "unsupported.upf").read_text(encoding="utf-8")

    document = parse_upf_text(text, path="unsupported.upf")

    assert [command.command for command in document.unsupported_commands] == ["create_supply_net"]
    assert [diagnostic.code for diagnostic in document.diagnostics] == [
        "unsupported_command",
        "unsupported_power_domain_option",
    ]
    assert document.diagnostics[0].location is not None
    assert document.diagnostics[0].location.line == 4
    assert document.diagnostics[1].evidence == ["-unknown_option", "value"]


def test_parser_handles_semicolon_commands_and_braced_elements() -> None:
    document = parse_upf_text(
        "set_scope /chip; create_power_domain PD_A -elements {u_a u_b}\n",
        path="inline.upf",
    )

    assert len(document.commands) == 2
    assert document.power_domains[0].scope == "/chip"
    assert document.power_domains[0].elements == ["u_a", "u_b"]
    assert document.commands[1].location.column == 18


def test_parser_reports_missing_required_arguments() -> None:
    document = parse_upf_text(
        "set_scope\ncreate_power_domain\ncreate_power_domain PD -elements\n",
        path="bad.upf",
    )

    assert [diagnostic.code for diagnostic in document.diagnostics] == [
        "missing_set_scope_argument",
        "missing_power_domain_name",
        "missing_power_domain_elements",
    ]
    assert document.diagnostics[2].location is not None
    assert document.diagnostics[2].location.line == 3
