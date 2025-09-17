#!/usr/bin/env python3
# wav_table_gen_cli.py — WAV → comma‑separated 0x?? text (CLI version)
# MIT‑like license, standard library only

import sys
import wave
import argparse
from pathlib import Path
from typing import List


MAX_FILES = 18
MAX_SECONDS = 20


def process_file(in_path: Path, output_dir: Path = None, verbose: bool = False, max_seconds: int = MAX_SECONDS) -> None:
    """Process a single WAV file and convert it to hex format."""
    if not in_path.exists():
        print(f"Error: File not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    if output_dir:
        out_path = output_dir / in_path.with_suffix(".txt").name
    else:
        out_path = in_path.with_suffix(".txt")

    try:
        with wave.open(str(in_path), "rb") as w:
            if w.getnchannels() != 1:
                print("Error: Stereo is not supported. Use mono.", file=sys.stderr)
                sys.exit(1)
            if w.getsampwidth() != 2:
                print("Error: Only 16‑bit PCM is supported.", file=sys.stderr)
                sys.exit(1)
            if w.getcomptype() != "NONE":
                print("Error: Compressed WAV is not supported.", file=sys.stderr)
                sys.exit(1)

            rate = w.getframerate()
            frames = min(rate * max_seconds, w.getnframes())  # up to max_seconds
            raw_bytes = w.readframes(frames)

        # Build comma‑separated 0x?? string
        hex_line = ",".join(f"0x{b:02X}" for b in raw_bytes)
        
        # Ensure output directory exists
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(hex_line)

        if verbose:
            print(f"Processed: {in_path.name}")
            print(f"  Sample rate: {rate} Hz")
            print(f"  Duration: {frames / rate:.2f} seconds")
            print(f"  Bytes: {len(raw_bytes)}")
        
        print(f"Wrote {len(raw_bytes)} bytes ({len(hex_line)} characters) to {out_path}")

    except wave.Error as e:
        print(f"Error processing {in_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error processing {in_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert WAV files to comma-separated hex format for embedded systems",
        epilog=f"Supports up to {MAX_FILES} files and {MAX_SECONDS} seconds per file. "
               "Only mono 16-bit PCM WAV files are supported."
    )
    
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="WAV files to process"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        help="Output directory for generated .txt files (default: same as input file)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed processing information"
    )
    
    parser.add_argument(
        "--max-seconds",
        type=int,
        default=MAX_SECONDS,
        help=f"Maximum seconds to process per file (default: {MAX_SECONDS})"
    )

    args = parser.parse_args()

    # Validate arguments
    if len(args.files) > MAX_FILES:
        print(f"Error: Too many files specified ({len(args.files)}). The limit is {MAX_FILES}.", file=sys.stderr)
        sys.exit(1)

    # Validate all files exist before processing any
    for file_path in args.files:
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        if file_path.suffix.lower() != ".wav":
            print(f"Warning: {file_path} doesn't have .wav extension", file=sys.stderr)

    # Process each file
    for file_path in args.files:
        process_file(file_path, args.output_dir, args.verbose, args.max_seconds)

    print(f"\nSuccessfully processed {len(args.files)} file(s)")


if __name__ == "__main__":
    main()
