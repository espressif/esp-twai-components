#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Espressif Systems (Shanghai) CO LTD
# SPDX-License-Identifier: Apache-2.0
"""Append a small Markdown table to the GitHub Actions step summary."""

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--row",
        nargs=2,
        action="append",
        default=None,
        metavar=("LABEL", "VALUE"),
    )
    parser.add_argument("--code-block-title")
    parser.add_argument("--code-block-content")
    args = parser.parse_args()
    if (args.code_block_title is None) != (args.code_block_content is None):
        parser.error(
            "--code-block-title and --code-block-content must be used together"
        )
    return args


def escape_table_cell(value: str) -> str:
    """Escape content that would otherwise change a Markdown table cell."""
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def code_fence(content: str) -> str:
    """Return a backtick fence that cannot be closed by content."""
    longest_run = max(
        (len(match.group()) for match in re.finditer(r"`+", content)),
        default=0,
    )
    return "`" * max(3, longest_run + 1)


def main() -> None:
    args = parse_args()
    rows = args.row or []
    lines = [f"## {args.title}", "", "| Parameter | Value |", "|-----------|-------|"]
    lines.extend(
        f"| {escape_table_cell(label)} | {escape_table_cell(value)} |"
        for label, value in rows
    )

    if args.code_block_content is not None:
        fence = code_fence(args.code_block_content)
        lines.extend(
            [
                "",
                f"### {args.code_block_title}",
                "",
                fence,
                args.code_block_content,
                fence,
            ]
        )

    with args.output.open("a", encoding="utf-8") as summary:
        summary.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
