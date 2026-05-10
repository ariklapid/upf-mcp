"""CLI entry point for upf-mcp."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from .server import create_server


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(levelname)s:%(name)s:%(message)s",
        stream=sys.stderr,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the UPF MCP server."""

    parser = argparse.ArgumentParser(description="Run the upf-mcp server.")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
        help=(
            "MCP transport to use. `stdio` is the default. `streamable-http` is "
            "experimental and requires --experimental-enable-http."
        ),
    )
    parser.add_argument(
        "--experimental-enable-http",
        action="store_true",
        help=(
            "Allow the experimental local streamable-http transport. This mode is not "
            "a hosted deployment and does not add authentication or workspace isolation."
        ),
    )
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        default="WARNING",
        help="Python logging level. Logs are written to stderr for stdio safety.",
    )
    args = parser.parse_args(argv)
    if args.transport == "streamable-http" and not args.experimental_enable_http:
        parser.error(
            "`streamable-http` is experimental and requires --experimental-enable-http. "
            "Use the default `stdio` transport for normal local MCP clients."
        )

    _configure_logging(args.log_level)
    create_server().run(args.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
