"""Command-line entry point for the THX-02 examples."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from thx02 import Client, choice

from decisionhello.demos import ALL_SCENARIOS, DEMO_SCENARIOS


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="decisionhello",
        description="Try text and image decision demos with HAL-X-AI/THX-02.",
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
        "--think",
        choices=("false", "auto", "true"),
        default="auto",
        help="model thinking mode (default: auto)",
    )

    classify_parser = commands.add_parser(
        "classify",
        help="classify a local image using your own candidate labels",
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
        "--think",
        choices=("false", "auto", "true"),
        default="auto",
        help="model thinking mode (default: auto)",
    )
    return parser


def _think_value(value: str) -> bool | str:
    """Convert the CLI thinking option to the value expected by thx02."""
    if value == "true":
        return True
    if value == "false":
        return False
    return "auto"


def _print_result(title: str, result: dict[str, Any]) -> None:
    """Print a named model response as readable JSON."""
    print(f"\n=== {title} ===")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def _run_demo(client: Client, scenario_name: str, think: bool | str) -> None:
    """Send one registered demo scenario to the THX-02 API."""
    scenario = DEMO_SCENARIOS[scenario_name]
    images = [str(scenario.image)] if scenario.image is not None else None
    result = client.decide(
        scenario.state,
        scenario.questions,
        images=images,
        think=think,
    )
    _print_result(scenario.title, result)


def _run_classify(
    client: Client,
    image_path: Path,
    labels: list[str],
    question: str,
    think: bool | str,
) -> None:
    """Classify a local image against user-supplied candidate labels."""
    result = client.decide(
        "Identify the main content in the supplied image.",
        {"classification": choice(question, labels)},
        images=[str(image_path)],
        think=think,
    )
    _print_result(f"Image classification: {image_path}", result)


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and run the requested demo."""
    parser = build_parser()
    args = parser.parse_args(argv)
    think = _think_value(args.think)

    if args.command == "demo":
        client = Client()
        scenario_names = ALL_SCENARIOS if args.scenario == "all" else (args.scenario,)
        for scenario_name in scenario_names:
            _run_demo(client, scenario_name, think)
        return 0

    if not args.image.is_file():
        parser.error(f"image file does not exist: {args.image}")
    labels = [label.strip() for label in args.labels.split(",") if label.strip()]
    if len(labels) < 2:
        parser.error("provide at least two non-empty comma-separated labels")
    if len(set(labels)) != len(labels):
        parser.error("candidate labels must be unique")

    client = Client()
    _run_classify(
        client,
        args.image,
        labels,
        args.question,
        think,
    )
    return 0
