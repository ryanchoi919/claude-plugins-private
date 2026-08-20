#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "trendspyg>=1.6.0",
# ]
# ///
"""CLI wrapper around trendspyg for relative Google Trends signals.

Self-contained (PEP 723): run via `uv run keyword_trends.py ...` and uv
resolves/caches trendspyg on the fly — no project-level dependency install
needed. Both subcommands never raise: any failure (rate limit, missing
Chrome, missing trendspyg, bad parameters) is reported as {"error": "..."}
on stdout with exit code 0, since this signal is an optional research aid,
not a pipeline gate. (uv itself failing to resolve the dependency — e.g.
fully offline with no cache — is outside this script's control and surfaces
as a non-zero exit from `uv run`, not from here.)
"""
import argparse
import json

try:
    import trendspyg
    _IMPORT_ERROR = None
except ImportError as exc:
    trendspyg = None
    _IMPORT_ERROR = f"trendspyg is not installed: {exc}"


def _emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def _emit_error(message):
    _emit({"error": message})


class _JSONErrorParser(argparse.ArgumentParser):
    """argparse raises SystemExit(2) + stderr on bad args by default;
    override so malformed CLI args become {"error": ...} + exit 0 too,
    matching every other failure path in this script."""

    def error(self, message):
        _emit_error(f"argument error: {message}")
        raise SystemExit(0)


def cmd_related(args):
    if trendspyg is None:
        _emit_error(_IMPORT_ERROR)
        return
    try:
        envelope = trendspyg.download_google_trends_explore(
            keyword=args.seed,
            geo=args.geo,
            include_related=True,
            include_geo=False,
        )
    except Exception as exc:
        _emit_error(str(exc))
        return

    related = envelope["related_queries"]
    _emit({
        "seed": args.seed,
        "geo": args.geo,
        "top": related["top"],
        "rising": related["rising"],
        "is_empty": envelope["is_empty"],
    })


def cmd_compare(args):
    if trendspyg is None:
        _emit_error(_IMPORT_ERROR)
        return
    try:
        envelope = trendspyg.download_google_trends_comparison(
            keywords=args.keywords,
            geo=args.geo,
            include_geo=False,
        )
    except Exception as exc:
        _emit_error(str(exc))
        return

    _emit({
        "keywords": envelope["keywords"],
        "geo": args.geo,
        "averages": envelope["averages"],
        "is_empty": not any(envelope["averages"].values()),
    })


def main():
    parser = _JSONErrorParser(
        description="Query relative Google Trends interest via trendspyg (0-100 index, not absolute volume)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    related_parser = subparsers.add_parser(
        "related", help="Related/rising search queries for a seed topic"
    )
    related_parser.add_argument("--seed", required=True)
    related_parser.add_argument("--geo", default="", help="ISO 3166-1 alpha-2 country code, or omit for worldwide")
    related_parser.set_defaults(func=cmd_related)

    compare_parser = subparsers.add_parser(
        "compare", help="Compare relative interest across 2-5 keywords"
    )
    compare_parser.add_argument("--keywords", nargs="+", required=True)
    compare_parser.add_argument("--geo", default="", help="ISO 3166-1 alpha-2 country code, or omit for worldwide")
    compare_parser.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
