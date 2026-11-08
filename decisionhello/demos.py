"""Reusable sample decision scenarios."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from thx02 import choice, noul, score

IMAGE_DIR = Path(__file__).resolve().parent.parent / "examples" / "images"


@dataclass(frozen=True)
class DemoScenario:
    """A state, its questions, and an optional image for one demo."""

    title: str
    state: str
    questions: dict[str, Any]
    image: Path | None = None


DEMO_SCENARIOS: dict[str, DemoScenario] = {
    "support": DemoScenario(
        title="Support ticket triage",
        state=(
            "I was charged three times after cancelling my trial. I contacted "
            "support last week and nobody replied. Please refund the extra "
            "charges or I will dispute them with my bank and close my account."
        ),
        questions={
            "team": choice(
                "Which team should handle this ticket?",
                billing="Charges, refunds, invoices, and subscriptions",
                technical="Bugs, errors, and account access problems",
                shipping="Deliveries and tracking",
            ),
            "urgency": score(
                "How urgent is this ticket?",
                ["low", "normal", "high", "urgent"],
            ),
            "refund": noul("Is the customer asking for money back?"),
        },
    ),
    "chart": DemoScenario(
        title="Read the chart",
        state="A bar chart of quarterly units sold. Which quarter has the highest sales?",
        questions={
            "highest_sales": choice(
                "Which quarter has the highest units sold?",
                ["Q1", "Q2", "Q3", "Q4"],
            ),
        },
        image=IMAGE_DIR / "chart.png",
    ),
    "spreadsheet": DemoScenario(
        title="Read the spreadsheet",
        state="A small store sales spreadsheet. Which product sold the most units?",
        questions={
            "top_product": choice(
                "Which product has the highest units sold?",
                ["Notebook", "Water bottle", "Desk lamp", "Floor mat"],
            ),
        },
        image=IMAGE_DIR / "spreadsheet.png",
    ),
    "dog": DemoScenario(
        title="Classify the dog picture",
        state="Identify the main object in this picture.",
        questions={
            "object": choice(
                "What is the main object?",
                ["dog", "bicycle", "mug", "other"],
            ),
        },
        image=IMAGE_DIR / "dog.png",
    ),
    "bicycle": DemoScenario(
        title="Classify the bicycle picture",
        state="Identify the main object in this picture.",
        questions={
            "object": choice(
                "What is the main object?",
                ["dog", "bicycle", "mug", "other"],
            ),
        },
        image=IMAGE_DIR / "bicycle.png",
    ),
    "mug": DemoScenario(
        title="Classify the mug picture",
        state="Identify the main object in this picture.",
        questions={
            "object": choice(
                "What is the main object?",
                ["dog", "bicycle", "mug", "other"],
            ),
        },
        image=IMAGE_DIR / "mug.png",
    ),
}

ALL_SCENARIOS = tuple(DEMO_SCENARIOS)
