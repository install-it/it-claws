import argparse
import sys
from pathlib import Path

import inquirer
from tqdm import tqdm

from .engine import ConcurrentPipeline
from .models import DownloadJob, ScrapeTarget
from .presets import ALL_TARGETS, get_target_names


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="it-claws")
    dl = parser.add_argument_group("Download Options")
    dl.add_argument("-o", "--output", type=Path, default=Path.cwd() / "downloads")

    tg = parser.add_argument_group("Target Options")
    mexcl = tg.add_mutually_exclusive_group()
    mexcl.add_argument("-t", "--targets", nargs="+", choices=get_target_names())
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
    ar.add_argument("-z", "--zip", type=Path, default=None, metavar="PATH",
                    help="Zip archive output path")
    ar.add_argument("-l", "--compress-level", type=int, choices=range(10), default=5,
                    help="Compression level (0-9)")
    ar.add_argument(
        "--zip-includes",
        action="append",
        nargs="+",
        type=str,
        default=None,
        metavar="PATHS",
        help="Additional files or directories to include in the archive",
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


def _resolve_names(names: list[str]) -> list[ScrapeTarget]:
    targets = []
    for name in names:
        target = next((t for t in ALL_TARGETS if t.name == name), None)
        if target is None:
            print(f"Unknown target: {name}", file=sys.stderr)
            sys.exit(1)
        targets.append(target)
    return targets


def resolve_selected_targets(
    target_names: list[str] | None,
    interactive: bool,
    all_targets: bool = False,
    target_from: Path | None = None,
) -> list[ScrapeTarget]:
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
        return _resolve_names(answers["targets"])

    if target_from:
        return _resolve_names(_parse_target_file(target_from))

    if all_targets and interactive:
        answers = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "targets",
                    message="Select drivers and utilities to download",
                    choices=[(n, n, True) for n in get_target_names()],
                ),
            ]
        )
        if not answers or not answers.get("targets"):
            tqdm.write("No targets selected interactively")
            return []
        return [t for t in ALL_TARGETS if t.name in answers["targets"]]

    if all_targets:
        return ALL_TARGETS

    if interactive:
        answers = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "targets",
                    message="Select drivers and utilities to download",
                    choices=get_target_names(),
                ),
            ]
        )
        if not answers or not answers.get("targets"):
            tqdm.write("No targets selected interactively")
            return []
        return [t for t in ALL_TARGETS if t.name in answers["targets"]]

    if target_names:
        return _resolve_names(target_names)

    return ALL_TARGETS


def run() -> None:
    parser = build_parser()
    args = parser.parse_args()

    targets = resolve_selected_targets(args.targets, args.interactive, args.all, args.target_from)
    if not targets:
        print("No valid targets to process", file=sys.stderr)
        sys.exit(1)

    if args.zip_includes and not args.zip:
        print("error: --zip-includes requires --zip", file=sys.stderr)
        sys.exit(1)

    jobs = [DownloadJob(target=t, output_root=args.output) for t in targets]
    results = ConcurrentPipeline(
        max_concurrent=args.max_concurrent,
        retries=args.retries,
        compress_level=args.compress_level,
    ).execute(jobs, args.output, args.zip, include=args.zip_includes)

    failed = [msg for _, success, msg in results if not success]

    if failed:
        for msg in failed:
            print(f"  FAILED: {msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run()
