"""Main CLI entry point for Okane."""

import argparse
import sys

from okane import __version__


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="okane",
        description="CLI tool for crawling political cash flow PDF reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--version", action="version", version=f"Okane {__version__}\nPython {sys.version}"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (can be repeated: -v, -vv, -vvv)",
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress non-error output"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Import crawl subcommand
    from okane.cli.crawl import setup_crawl_parser

    setup_crawl_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute subcommand
    if args.command == "crawl":
        from okane.cli.crawl import handle_crawl

        exit_code = handle_crawl(args)
        sys.exit(exit_code)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
