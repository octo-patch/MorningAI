"""Pluggable image generation for ai-tracker.

Dispatches to external APIs (Gemini, GPT, MiniMax) or skips (none).
Provider is selected via IMAGE_GEN_PROVIDER env var.
"""

import base64
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import http
from .env import get_key

IMAGE_GEN_TIMEOUT = 120


def _log(msg: str):
    sys.stderr.write(f"[ImageGen] {msg}\n")
    sys.stderr.flush()


class ImageGenError(Exception):
    pass


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

def _generate_none(prompt: str, output_path: str, config: Dict[str, Any]) -> str:
    """No-op provider — skip image generation."""
    _log("Provider is 'none', skipping image generation")
    return ""


def _generate_gemini(prompt: str, output_path: str, config: Dict[str, Any]) -> str:
    """Generate image via Google Gemini (Imagen) API."""
    api_key = get_key(config, "GEMINI_API_KEY")
    if not api_key:
        raise ImageGenError("GEMINI_API_KEY not configured")

    model = get_key(config, "GEMINI_IMAGE_MODEL") or "imagen-3.0-generate-002"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": "16:9",
            "sampleCount": 1,
        },
    }

    _log(f"Calling Gemini Imagen ({model})...")
    try:
        response = http.post(url, json_data=payload, headers=headers, timeout=IMAGE_GEN_TIMEOUT)
    except http.HTTPError as e:
        raise ImageGenError(f"Gemini API error: {e}") from e

    predictions = response.get("predictions", [])
    if not predictions:
        raise ImageGenError("Gemini returned no predictions")

    b64_data = predictions[0].get("bytesBase64Encoded", "")
    if not b64_data:
        raise ImageGenError("Gemini response missing image data")

    _write_image(b64_data, output_path)
    _log(f"Gemini image saved to {output_path}")
    return output_path


def _generate_gpt(prompt: str, output_path: str, config: Dict[str, Any]) -> str:
    """Generate image via OpenAI (gpt-image-1 / DALL-E) API."""
    api_key = get_key(config, "OPENAI_API_KEY")
    if not api_key:
        raise ImageGenError("OPENAI_API_KEY not configured")

    model = get_key(config, "OPENAI_IMAGE_MODEL") or "gpt-image-1"
    size = get_key(config, "OPENAI_IMAGE_SIZE") or "1536x1024"
    url = "https://api.openai.com/v1/images/generations"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }

    _log(f"Calling OpenAI ({model}, size={size})...")
    try:
        response = http.post(url, json_data=payload, headers=headers, timeout=IMAGE_GEN_TIMEOUT)
    except http.HTTPError as e:
        raise ImageGenError(f"OpenAI API error: {e}") from e

    data = response.get("data", [])
    if not data:
        raise ImageGenError("OpenAI returned no image data")

    b64_data = data[0].get("b64_json", "")
    if not b64_data:
        raise ImageGenError("OpenAI response missing b64_json")

    _write_image(b64_data, output_path)
    _log(f"GPT image saved to {output_path}")
    return output_path


def _generate_minimax(prompt: str, output_path: str, config: Dict[str, Any]) -> str:
    """Generate image via MiniMax API."""
    api_key = get_key(config, "MINIMAX_API_KEY")
    if not api_key:
        raise ImageGenError("MINIMAX_API_KEY not configured")

    model = get_key(config, "MINIMAX_IMAGE_MODEL") or "image-01"
    url = "https://api.minimax.chat/v1/image_generation"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "response_format": "b64_json",
        "n": 1,
    }

    _log(f"Calling MiniMax ({model})...")
    try:
        response = http.post(url, json_data=payload, headers=headers, timeout=IMAGE_GEN_TIMEOUT)
    except http.HTTPError as e:
        raise ImageGenError(f"MiniMax API error: {e}") from e

    data = response.get("data", {})
    image_list = data.get("image_base64", [])
    if not image_list:
        raise ImageGenError("MiniMax returned no image data")

    b64_data = image_list[0] if isinstance(image_list, list) else image_list
    if not b64_data:
        raise ImageGenError("MiniMax response missing image data")

    _write_image(b64_data, output_path)
    _log(f"MiniMax image saved to {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

PROVIDERS = {
    "none": _generate_none,
    "gemini": _generate_gemini,
    "gpt": _generate_gpt,
    "minimax": _generate_minimax,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate(prompt: str, output_path: str, config: Dict[str, Any]) -> str:
    """Generate an image using the configured provider.

    Args:
        prompt: Image generation prompt text
        output_path: Path to save the output PNG
        config: Configuration dict (from env.get_config())

    Returns:
        Output file path on success, empty string if skipped (none provider)

    Raises:
        ImageGenError: On API or configuration errors
    """
    provider_name = get_key(config, "IMAGE_GEN_PROVIDER") or "none"

    if provider_name not in PROVIDERS:
        available = ", ".join(sorted(PROVIDERS.keys()))
        raise ImageGenError(f"Unknown provider '{provider_name}'. Available: {available}")

    provider_fn = PROVIDERS[provider_name]
    return provider_fn(prompt, output_path, config)


def list_providers() -> list:
    """Return list of available provider names."""
    return sorted(PROVIDERS.keys())


def generate_batch(
    items: List[Dict[str, str]],
    config: Dict[str, Any],
) -> List[str]:
    """Generate multiple images sequentially.

    Args:
        items: List of {"prompt": str, "output": str} dicts.
               Entries with empty prompt are skipped.
        config: Configuration dict (from env.get_config())

    Returns:
        List of successfully generated file paths (empty strings for skipped)
    """
    results = []
    total = len(items)

    for i, item in enumerate(items):
        prompt = item.get("prompt", "").strip()
        output_path = item.get("output", "")

        if not prompt:
            _log(f"[{i + 1}/{total}] Skipping (empty prompt): {output_path}")
            results.append("")
            continue

        if not output_path:
            _log(f"[{i + 1}/{total}] Skipping (no output path)")
            results.append("")
            continue

        _log(f"[{i + 1}/{total}] Generating: {output_path}")
        try:
            result = generate(prompt, output_path, config)
            results.append(result)
        except ImageGenError as e:
            _log(f"[{i + 1}/{total}] Failed: {e}")
            results.append("")

    succeeded = sum(1 for r in results if r)
    _log(f"Batch complete: {succeeded}/{total} images generated")
    return results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_image(b64_data: str, output_path: str):
    """Decode base64 image data and write to file."""
    try:
        image_bytes = base64.b64decode(b64_data)
    except Exception as e:
        raise ImageGenError(f"Failed to decode base64 image data: {e}") from e

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image_bytes)
