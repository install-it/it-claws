import argparse
import asyncio
import logging
import sys
from pathlib import Path

import inquirer

from .engine import ConcurrentPipeline
from .models import DownloadJob, ScrapeTarget
from .presets import ALL_TARGETS, get_target_names

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="it-claws")
    dl = parser.add_argument_group("Download Options")
    dl.add_argument("-o", "--output", type=Path, default=Path.cwd() / "downloads")
    dl.add_argument("-f", "--folder", type=str, default=None)
    dl.add_argument("--max-concurrent", type=int, default=5)

    tg = parser.add_argument_group("Target Options")
    mexcl = tg.add_mutually_exclusive_group()
    mexcl.add_argument("-t", "--targets", nargs="+", choices=get_target_names())
    mexcl.add_argument("--all", action="store_true", help="Select all available targets")
    mexcl.add_argument("--target-from", type=Path, metavar="FILE",
                       help="Read target names from a text file (one per line, # for comments)")
    tg.add_argument("-i", "--interactive", action="store_true")

    ra = parser.add_argument_group("Resilience & Archiving Options")
    ra.add_argument("--retries", type=int, default=1)
    ra.add_argument("-a", "--archive-path", type=Path, default=None)
    ra.add_argument("-l", "--compress-level", type=int, choices=range(10), default=5)

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
            logger.error("Unknown target: %s", name)
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
            logger.warning("No targets selected interactively")
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
            logger.warning("No targets selected interactively")
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
            logger.warning("No targets selected interactively")
            return []
        return [t for t in ALL_TARGETS if t.name in answers["targets"]]

    if target_names:
        return _resolve_names(target_names)

    return ALL_TARGETS


async def run_pipeline(
    targets: list[ScrapeTarget],
    output_root: Path,
    custom_folder: str | None,
    max_concurrent: int,
    retries: int,
    archive_path: Path | None,
    compress_level: int,
) -> list[tuple[DownloadJob, bool, str]]:
    jobs = [
        DownloadJob(target=t, output_root=output_root, custom_folder=custom_folder) for t in targets
    ]
    return await ConcurrentPipeline(
        max_downloads=max_concurrent, retries=retries, compress_level=compress_level
    ).run(jobs, output_root, archive_path)


def run() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    targets = resolve_selected_targets(args.targets, args.interactive, args.all, args.target_from)
    if not targets:
        logger.error("No valid targets to process")
        sys.exit(1)

    logger.info("Starting pipeline with %d target(s)", len(targets))
    logger.info("Output directory: %s", args.output)

    results = asyncio.run(
        run_pipeline(
            targets=targets,
            output_root=args.output,
            custom_folder=args.folder,
            max_concurrent=args.max_concurrent,
            retries=args.retries,
            archive_path=args.archive_path,
            compress_level=args.compress_level,
        )
    )

    failed = [msg for _, success, msg in results if not success]
    logger.info(
        "Pipeline complete: %d succeeded, %d failed",
        len(results) - len(failed),
        len(failed),
    )

    if failed:
        for msg in failed:
            print(f"  FAILED: {msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run()
