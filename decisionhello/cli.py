"""Command-line entry point for the THX-02 examples."""

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol

from thx02 import choice

from decisionhello.demos import ALL_SCENARIOS, DEMO_SCENARIOS

MODEL_REPO = "HAL-X-AI/THX-02"
MODEL_IGNORE_PATTERNS = ["thinker/*", "mobile/*", "assets/*"]


class DecisionModel(Protocol):
    """The local model interface used by the demos."""

    def decide(
        self,
        state: str,
        questions: dict[str, Any],
        *,
        images: list[str] | None = None,
    ) -> dict[str, Any]: ...


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="decisionhello",
        description="Run text and image decision demos locally with HAL-X-AI/THX-02.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    demo_parser = commands.add_parser("demo", help="run an included demo")
    demo_parser.add_argument(
        "--scenario",
        choices=("all", *ALL_SCENARIOS),
        default="support",
        help="which demo to run (default: support)",
    )
    demo_parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="inference device (default: use CUDA when available, otherwise CPU)",
    )

    classify_parser = commands.add_parser(
        "classify",
        help="classify a local image offline using your own candidate labels",
    )
    classify_parser.add_argument("image", type=Path, help="path to a local image")
    classify_parser.add_argument(
        "--labels",
        default="dog,bicycle,mug,chart,spreadsheet,other",
        help="comma-separated candidate labels",
    )
    classify_parser.add_argument(
        "--question",
        default="What is the main object or content shown?",
        help="question to ask about the image",
    )
    classify_parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="inference device (default: use CUDA when available, otherwise CPU)",
    )
    return parser


def _load_model(device: str) -> DecisionModel:
    """Load THX-02 from the local cache, downloading its weights only if needed."""
    from huggingface_hub import snapshot_download
    from huggingface_hub.errors import LocalEntryNotFoundError

    try:
        model_path = snapshot_download(
            MODEL_REPO,
            ignore_patterns=MODEL_IGNORE_PATTERNS,
            local_files_only=True,
        )
    except LocalEntryNotFoundError:
        print(
            "THX-02 is not cached. Downloading approximately 9 GB from Hugging Face "
            "for offline use after setup.",
            file=sys.stderr,
        )
        model_path = snapshot_download(
            MODEL_REPO,
            ignore_patterns=MODEL_IGNORE_PATTERNS,
        )

    if device == "auto":
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading THX-02 from the local cache on {device}.", file=sys.stderr)
    from thx02 import THX02

    return THX02.load(model_path, device=device)


def _print_result(title: str, result: dict[str, Any]) -> None:
    """Print a named model response as readable JSON."""
    print(f"\n=== {title} ===")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def _run_demo(model: DecisionModel, scenario_name: str) -> None:
    """Run one registered demo scenario with the local THX-02 model."""
    scenario = DEMO_SCENARIOS[scenario_name]
    images = [str(scenario.image)] if scenario.image is not None else None
    result = model.decide(
        scenario.state,
        scenario.questions,
        images=images,
    )
    _print_result(scenario.title, result)


def _run_classify(
    model: DecisionModel,
    image_path: Path,
    labels: list[str],
    question: str,
) -> None:
    """Classify a local image against user-supplied candidate labels."""
    result = model.decide(
        "Identify the main content in the supplied image.",
        {"classification": choice(question, labels)},
        images=[str(image_path)],
    )
    _print_result(f"Image classification: {image_path}", result)


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and run the requested demo."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "demo":
        model = _load_model(args.device)
        scenario_names = ALL_SCENARIOS if args.scenario == "all" else (args.scenario,)
        for scenario_name in scenario_names:
            _run_demo(model, scenario_name)
        return 0

    if not args.image.is_file():
        parser.error(f"image file does not exist: {args.image}")
    labels = [label.strip() for label in args.labels.split(",") if label.strip()]
    if len(labels) < 2:
        parser.error("provide at least two non-empty comma-separated labels")
    if len(set(labels)) != len(labels):
        parser.error("candidate labels must be unique")

    model = _load_model(args.device)
    _run_classify(
        model,
        args.image,
        labels,
        args.question,
    )
    return 0
