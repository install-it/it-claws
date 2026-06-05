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
    parser = argparse.ArgumentParser(
        prog="it-claws",
        description="Automated concurrent companion scraper for staging PC deployment environments",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path.cwd() / "downloads",
        help="Output directory for downloaded files (default: ./downloads)",
    )
    parser.add_argument(
        "-t",
        "--targets",
        nargs="+",
        choices=get_target_names(),
        help="Specific targets to download (space-separated)",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Launch interactive target selection prompt",
    )
    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        default=None,
        help="Custom folder name for all downloads",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging output",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent downloads (default: 5)",
    )
    return parser


def resolve_selected_targets(
    target_names: list[str] | None,
    interactive: bool,
) -> list[ScrapeTarget]:
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
        targets = []
        for name in target_names:
            target = next((t for t in ALL_TARGETS if t.name == name), None)
            if target is None:
                logger.error("Unknown target: %s", name)
                sys.exit(1)
            targets.append(target)
        return targets

    return ALL_TARGETS


async def run_pipeline(
    targets: list[ScrapeTarget],
    output_root: Path,
    custom_folder: str | None,
    max_concurrent: int,
) -> list[tuple[DownloadJob, bool, str]]:
    jobs = [
        DownloadJob(target=t, output_root=output_root, custom_folder=custom_folder) for t in targets
    ]
    return await ConcurrentPipeline(max_downloads=max_concurrent).run(jobs, output_root)


def run() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    targets = resolve_selected_targets(args.targets, args.interactive)
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
