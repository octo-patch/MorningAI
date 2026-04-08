#!/usr/bin/env python3
"""Generate cover and per-type infographics via external image generation API.

Supports single-image mode (--prompt) and batch mode (--batch manifest.json).

Usage:
    # Single image
    python3 skills/gen-infographic/scripts/gen_infographic.py --prompt "16:9 infographic, AI News Daily ..." -o cover.png

    # Batch mode (multiple images from manifest)
    python3 skills/gen-infographic/scripts/gen_infographic.py --batch manifest.json

    # Pipe prompt via stdin
    echo "prompt text" | python3 skills/gen-infographic/scripts/gen_infographic.py --provider gpt

Manifest JSON format:
    [
      {"prompt": "16:9 infographic, AI News Daily ...", "output": "news_infographic_2026-04-08.png"},
      {"prompt": "16:9 infographic, Model Updates ...", "output": "news_infographic_2026-04-08_model.png"}
    ]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib import env
from lib.image_gen import generate, generate_batch, list_providers, ImageGenError


def _log(msg: str):
    sys.stderr.write(f"[gen-infographic] {msg}\n")
    sys.stderr.flush()


def _run_single(args, config):
    """Single-image mode: one prompt → one image."""
    # Read prompt
    if args.prompt:
        prompt = args.prompt
    elif args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    else:
        _log("Error: No prompt provided. Use --prompt, --prompt-file, or pipe to stdin.")
        sys.exit(1)

    if not prompt:
        _log("Error: Empty prompt")
        sys.exit(1)

    output_path = args.output or f"news_infographic_{args.date}.png"
    provider_name = config.get("IMAGE_GEN_PROVIDER", "none")
    _log(f"Provider: {provider_name}, Output: {output_path}")

    try:
        result = generate(prompt, output_path, config)
    except ImageGenError as e:
        _log(f"Error: {e}")
        sys.exit(1)

    if result:
        _log(f"Success: {result}")
        print(result)
    else:
        _log("Skipped (provider=none)")


def _run_batch(args, config):
    """Batch mode: manifest JSON → multiple images."""
    manifest_path = Path(args.batch)
    if not manifest_path.exists():
        _log(f"Error: Manifest file not found: {args.batch}")
        sys.exit(1)

    try:
        items = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        _log(f"Error: Failed to read manifest: {e}")
        sys.exit(1)

    if not isinstance(items, list):
        _log("Error: Manifest must be a JSON array of {\"prompt\": ..., \"output\": ...}")
        sys.exit(1)

    provider_name = config.get("IMAGE_GEN_PROVIDER", "none")
    _log(f"Batch mode: {len(items)} images, provider: {provider_name}")

    results = generate_batch(items, config)
    succeeded = [r for r in results if r]

    for path in succeeded:
        print(path)

    _log(f"Done: {len(succeeded)}/{len(items)} images generated")
    if not succeeded and provider_name != "none":
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate infographics via external API")
    parser.add_argument("--prompt", "-p", default=None,
                        help="Image generation prompt text (single-image mode)")
    parser.add_argument("--prompt-file", default=None,
                        help="Path to file containing the prompt (single-image mode)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output PNG file path (default: news_infographic_{date}.png)")
    parser.add_argument("--batch", default=None,
                        help="Path to manifest JSON for batch generation")
    parser.add_argument("--provider", default=None,
                        choices=list_providers(),
                        help="Image generation provider (overrides IMAGE_GEN_PROVIDER env var)")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Date for default output filename (default: today)")
    args = parser.parse_args()

    # Load config and apply provider override
    config = env.get_config()
    if args.provider:
        config["IMAGE_GEN_PROVIDER"] = args.provider

    if args.batch:
        _run_batch(args, config)
    else:
        _run_single(args, config)


if __name__ == "__main__":
    main()
