import argparse
import os
import pickle
import shutil
import sys
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from typing import Iterable

import patoolib

import config
from archive import Archive7zip, ArchivePowershell, ArchivePyZipFile
from driver_claw import DriverClaw


@contextmanager
def setup_print(silent: bool):
    """Context manager to control console output.

    Args:
        silent (bool): Suppress output if True.
    """
    if silent:
        with open(os.devnull, 'w') as f, redirect_stdout(f):
            yield
    else:
        yield


def validate_ext(choices: Iterable[str], fname: str):
    """Validate file extension for configuration files.

    Args:
        choices (Iterable[str]): Allowed file extensions.
        fname (str): File name to validate.

    Returns:
        str: Validated file name.

    Raises:
        argparse.ArgumentTypeError: If file extension is invalid.
    """
    ext = os.path.splitext(fname)[1][1:].lower()
    if ext not in choices:
        raise argparse.ArgumentTypeError(
            f'Invalid file extension: ".{ext}". Expected one of: {', '.join(choices)}.')
    return fname


if __name__ == '__main__':
    # set proper CWD
    os.chdir(Path(sys.executable).parent
             if getattr(sys, 'frozen', False)
             else Path(__file__).parents[1])

    parser = argparse.ArgumentParser(
        description='Find and download the latest common hardware drivers, and diagnostic tool.')
    parser.add_argument(
        '-d', '--download-dir', type=str, default='downloads',
        help='Directory for downloads (default: downloads)'
    )
    parser.add_argument(
        '-e', '--error-handling', choices=['exit', 'ignore', 'log'], default='log',
        help='How to handle download errors: exit (stop on error), ignore (continue), log (log failures and continue)'
    )
    parser.add_argument(
        '-r', '--retry-failed', action='store_true',
        help='Retry failed downloads from previous run'
    )
    parser.add_argument(
        '-o', '--archive-path', type=str, default='driver-pack.zip',
        help='Path for the produced archive file (default: ./driver-pack.zip)'
    )
    parser.add_argument(
        '-l', '--compress-level', type=int, default=5, choices=range(0, 10),
        help='Compression level for the archive (0-9, default: 5)'
    )
    parser.add_argument(
        '-i', '--include-file', type=str, nargs='+', action='extend',
        help='Additional files or directories to include in archive'
    )
    parser.add_argument(
        '-s', '--silent', action='store_true', help='Suppress all output messages'
    )
    parser.add_argument(
        '-c', '--claw-config', type=lambda s: validate_ext(('py', 'json', 'pkl'), s),
        default='claw_prizes.pkl',
        help='Path to configuration file (.json, .py, or .pkl)'
    )
    parser.add_argument(
        '--configure', action='store_true',
        help='Interactive configuration mode to select drivers'
    )
    parser.add_argument(
        '-w', '--web-driver', default='Firefox',
        choices=['Chrome', 'Edge', 'Firefox'],
        help='Select the web driver to use'
    )

    group_archive = parser.add_mutually_exclusive_group()
    group_archive.add_argument(
        '--archive-only', action='store_true',
        help='Only create archive from existing output directory, skip scraping'
    )
    group_archive.add_argument(
        '--no-archive', action='store_true',
        help='Skip creating zip archive'
    )

    args = parser.parse_args()

    with setup_print(args.silent):
        if args.configure:
            config_file = Path(args.claw_config or 'claw_config.pkl')

            print('Starting interactive configuration...')
            selections = config.configurate()
            with open(config_file, 'wb') as f:
                pickle.dump(selections, f)

            print(f'Configuration is saved to "{config_file.absolute()}"')
            sys.exit(0)

        try:
            path_7zip = Path('bin', '7zip', '7za.exe')

            archive = Archive7zip(path_7zip
                                  if path_7zip.exists()
                                  else patoolib.find_archive_program("7z", "unzip"))

            print(
                f'Using "{archive.path_7zip.absolute()}" as the archive handler.')
        except patoolib.util.PatoolError:
            print(
                'Unable to locate any 7zip executable, fell back to use Python built-in zip library as the archive handler.')
            archive = ArchivePyZipFile()

        if not args.archive_only:
            if not args.retry_failed and os.path.exists(args.download_dir):
                shutil.rmtree(args.download_dir)

            claw = DriverClaw.from_file(
                archive=archive, driver_name=args.web_driver,
                prizes_path=(Path(args.download_dir, '.failedclaws.pkl')
                             if args.retry_failed
                             else Path(args.claw_config)),
                destination=Path(args.download_dir))
            failed = claw.start(args.error_handling == 'exit')

            if len(failed) > 0:
                if args.error_handling == 'log':
                    print(
                        f'Failed to download {len(failed)} file(s). Use --retry-failed to retry.')

                    with open(Path(args.download_dir, '.failedclaws.pkl'), 'wb') as f:
                        pickle.dump(failed, f)

                if args.error_handling != 'ignore':
                    sys.exit(1)
            else:
                Path(args.download_dir, '.failedclaws.pkl').unlink(True)

            if args.no_archive:
                sys.exit(0)

        if not os.path.exists(args.download_dir):
            print(
                f'Error: Output directory "{args.download_dir}" does not exist.')
            sys.exit(1)
        if not os.listdir(args.download_dir):
            print(f'Error: Output directory "{args.download_dir}" is empty.')
            sys.exit(1)

        print(f'Archiving downloaded files into "{args.archive_path}".')
        archive.zip(args.archive_path,
                    *(args.include_file or []),
                    args.download_dir,
                    level=args.compress_level,
                    silent=args.silent)
