import argparse
import sys
from pathlib import Path

import inquirer
from tqdm import tqdm

from .engine import ConcurrentPipeline
from .models import DownloadJob, ScrapeTarget
from .presets import expand_selection, get_selection_choices


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="it-claws")
    dl = parser.add_argument_group("Download Options")
    dl.add_argument("-o", "--output", type=Path, default=Path.cwd() / "downloads")
    dl.add_argument(
        "-c",
        "--clear-output",
        action="store_true",
        help="Remove output directory before starting",
    )

    tg = parser.add_argument_group("Target Options")
    mexcl = tg.add_mutually_exclusive_group()
    mexcl.add_argument("-t", "--targets", nargs="+", choices=get_selection_choices())
    mexcl.add_argument("--all", action="store_true", help="Select all available targets")
    mexcl.add_argument(
        "--target-from",
        type=Path,
        metavar="FILE",
        help="Read target names from a text file (one per line, # for comments)",
    )
    tg.add_argument("-i", "--interactive", action="store_true")

    rs = parser.add_argument_group("Resilience Options")
    rs.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Max parallel downloads (default: 3, 1 = sequential)",
    )
    rs.add_argument(
        "--retries",
        type=int,
        default=1,
        help="Full re-scrape passes for failed entries (0 = run once, no retry)",
    )

    ar = parser.add_argument_group("Archiving Options")
    ar.add_argument(
        "-z", "--zip", type=Path, default=None, metavar="PATH", help="Zip archive output path"
    )
    ar.add_argument(
        "-l",
        "--compress-level",
        type=int,
        choices=range(10),
        default=5,
        help="Compression level (0-9)",
    )
    ar.add_argument(
        "--zip-prefix",
        type=str,
        default=None,
        metavar="PREFIX",
        help="Control how the output directory is represented in the ZIP. "
        "Default: strip the output directory name. "
        "Specify a name to prefix all entries (e.g. --zip-prefix pkg).",
    )
    ar.add_argument(
        "--zip-include",
        action="append",
        type=str,
        default=None,
        metavar="SOURCE[=LAYOUT]",
        help="Additional files or directories to include in the archive. "
        "Format: <source>[=<layout>]. Can be specified multiple times.",
    )
    ar.add_argument(
        "--manifest",
        action="store_true",
        help="Generate manifest.json inside the archive (required by install-it)",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def _parse_target_file(path: Path) -> list[str]:
    names = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.append(line)
    return names


def resolve_selected_targets(
    target_names: list[str] | None,
    interactive: bool,
    all_targets: bool = False,
    target_from: Path | None = None,
) -> list[tuple[ScrapeTarget, str | None]]:
    if target_from and interactive:
        names = _parse_target_file(target_from)
        answers = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "targets",
                    message="Select drivers and utilities to download",
                    choices=[(n, n, True) for n in names],
                ),
            ]
        )
        if not answers or not answers.get("targets"):
            tqdm.write("No targets selected interactively")
            return []
        return expand_selection(answers["targets"])

    if target_from:
        return expand_selection(_parse_target_file(target_from))

    if all_targets and interactive:
        answers = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "targets",
                    message="Select drivers and utilities to download",
                    choices=[(n, n, True) for n in get_selection_choices()],
                ),
            ]
        )
        if not answers or not answers.get("targets"):
            tqdm.write("No targets selected interactively")
            return []
        return expand_selection(answers["targets"])

    if all_targets:
        return expand_selection(get_selection_choices())

    if interactive:
        answers = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "targets",
                    message="Select drivers and utilities to download",
                    choices=get_selection_choices(),
                ),
            ]
        )
        if not answers or not answers.get("targets"):
            tqdm.write("No targets selected interactively")
            return []
        return expand_selection(answers["targets"])

    if target_names:
        return expand_selection(target_names)

    return expand_selection(get_selection_choices())


def run() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.output.exists() and not args.clear_output:
        tqdm.write(
            f"Output directory {args.output} already exists. "
            "Use -c, --clear-output to clear it, or remove it manually.",
        )
        sys.exit(1)

    if args.clear_output and args.output.exists():
        import shutil

        shutil.rmtree(args.output)

    targets = resolve_selected_targets(args.targets, args.interactive, args.all, args.target_from)
    if not targets:
        tqdm.write("No valid targets to process")
        sys.exit(1)

    if args.zip_include and not args.zip:
        tqdm.write("error: --zip-include requires --zip")
        sys.exit(1)

    results = ConcurrentPipeline(
        max_concurrent=args.max_concurrent,
        retries=args.retries,
        compress_level=args.compress_level,
    ).execute(
        [DownloadJob(target=t, output_root=args.output, name=name) for t, name in targets],
        args.output,
        args.zip,
        zip_prefix=args.zip_prefix,
        zip_includes=args.zip_include,
        manifest=args.manifest,
    )

    if failed := [msg for _, success, msg in results if not success]:
        for msg in failed:
            tqdm.write(f"  FAILED: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    run()
