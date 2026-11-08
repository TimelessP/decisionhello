"""Tests for registered scenarios and command-line argument handling."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from decisionhello.cli import _think_value, main
from decisionhello.demos import ALL_SCENARIOS, DEMO_SCENARIOS


class DemoScenarioTests(unittest.TestCase):
    """Verify the built-in scenarios are ready to run."""

    def test_all_image_scenarios_point_to_existing_pngs(self) -> None:
        """Every image demo has a checked-in image file."""
        for scenario in DEMO_SCENARIOS.values():
            if scenario.image is not None:
                with self.subTest(image=scenario.image.name):
                    self.assertTrue(scenario.image.is_file())
                    self.assertEqual(scenario.image.suffix, ".png")

    def test_all_scenarios_have_questions(self) -> None:
        """Each demo defines at least one decision question."""
        self.assertEqual(len(ALL_SCENARIOS), 6)
        for name, scenario in DEMO_SCENARIOS.items():
            with self.subTest(scenario=name):
                self.assertTrue(scenario.questions)


class CommandLineTests(unittest.TestCase):
    """Verify parser settings and API call wiring without network requests."""

    def test_default_command_runs_support_demo(self) -> None:
        """The no-options demo command uses support triage."""
        client = Mock()
        client.decide.return_value = {"answers": {}}
        with patch("decisionhello.cli.Client", return_value=client):
            self.assertEqual(main(["demo"]), 0)
        self.assertEqual(client.decide.call_count, 1)
        self.assertIsNone(client.decide.call_args.kwargs["images"])
        self.assertEqual(client.decide.call_args.kwargs["think"], "auto")

    def test_classify_requires_two_distinct_labels(self) -> None:
        """Invalid label sets fail before making an API request."""
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "photo.png"
            image.touch()
            client = Mock()
            with self.assertRaises(SystemExit) as error:
                with patch("decisionhello.cli.Client", return_value=client):
                    with contextlib.redirect_stderr(io.StringIO()):
                        main(["classify", str(image), "--labels", "dog,dog"])
        self.assertEqual(error.exception.code, 2)
        client.decide.assert_not_called()

    def test_classify_sends_image_and_custom_labels(self) -> None:
        """A valid image classification forwards the chosen labels and path."""
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "photo.png"
            image.touch()
            client = Mock()
            client.decide.return_value = {"answers": {}}
            with patch("decisionhello.cli.Client", return_value=client):
                self.assertEqual(
                    main(
                        [
                            "classify",
                            str(image),
                            "--labels",
                            "dog,cat,other",
                            "--question",
                            "Which animal is shown?",
                        ]
                    ),
                    0,
                )
        self.assertEqual(client.decide.call_args.args[0], "Identify the main content in the supplied image.")
        self.assertEqual(
            client.decide.call_args.kwargs["images"],
            [str(image)],
        )
        self.assertEqual(
            client.decide.call_args.args[1]["classification"]["criteria"],
            {"dog": "dog", "cat": "cat", "other": "other"},
        )

    def test_think_option_conversion(self) -> None:
        """CLI values map to the client's supported thinking values."""
        self.assertIs(_think_value("true"), True)
        self.assertIs(_think_value("false"), False)
        self.assertEqual(_think_value("auto"), "auto")


if __name__ == "__main__":
    unittest.main()
