"""Tests for registered scenarios and command-line argument handling."""

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from decisionhello.cli import MODEL_REPO, _load_model, main
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
    """Verify parser settings and local model wiring without network requests."""

    def test_default_command_runs_support_demo(self) -> None:
        """The default demo loads the local model and runs support triage."""
        model = Mock()
        model.decide.return_value = {"answers": {}}
        with patch("decisionhello.cli._load_model", return_value=model) as load_model:
            self.assertEqual(main(["demo"]), 0)
        load_model.assert_called_once_with("auto")
        self.assertEqual(model.decide.call_count, 1)
        self.assertIsNone(model.decide.call_args.kwargs["images"])

    def test_classify_requires_two_distinct_labels(self) -> None:
        """Invalid label sets fail before loading the local model."""
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "photo.png"
            image.touch()
            with self.assertRaises(SystemExit) as error:
                with patch("decisionhello.cli._load_model") as load_model:
                    with contextlib.redirect_stderr(io.StringIO()):
                        main(["classify", str(image), "--labels", "dog,dog"])
        self.assertEqual(error.exception.code, 2)
        load_model.assert_not_called()

    def test_classify_sends_image_and_custom_labels(self) -> None:
        """A valid classification forwards its image and labels to the local model."""
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "photo.png"
            image.touch()
            model = Mock()
            model.decide.return_value = {"answers": {}}
            with patch("decisionhello.cli._load_model", return_value=model):
                self.assertEqual(
                    main(
                        [
                            "classify",
                            str(image),
                            "--labels",
                            "dog,cat,other",
                            "--question",
                            "Which animal is shown?",
                            "--device",
                            "cpu",
                        ]
                    ),
                    0,
                )
        self.assertEqual(model.decide.call_args.args[0], "Identify the main content in the supplied image.")
        self.assertEqual(
            model.decide.call_args.kwargs["images"],
            [str(image)],
        )
        self.assertEqual(
            model.decide.call_args.args[1]["classification"]["criteria"],
            {"dog": "dog", "cat": "cat", "other": "other"},
        )
        with patch("decisionhello.cli._load_model", return_value=model) as load_model:
            main(["demo", "--device", "cpu"])
        load_model.assert_called_once_with("cpu")

    def test_model_load_checks_cache_before_downloading(self) -> None:
        """A cached checkpoint is loaded from its local path without downloading."""
        cached_path = "/tmp/thx02-cache"
        with (
            patch("huggingface_hub.snapshot_download", return_value=cached_path) as download,
            patch("torch.cuda.is_available", return_value=False),
            patch("thx02.THX02.load", return_value=Mock()) as load,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            _load_model("auto")

        download.assert_called_once_with(
            MODEL_REPO,
            ignore_patterns=["thinker/*", "mobile/*", "assets/*"],
            local_files_only=True,
        )
        load.assert_called_once_with(cached_path, device="cpu")

    def test_cpu_model_load_disables_cuda_kernels(self) -> None:
        """CPU loading prevents CUDA-only kernels from being selected."""
        sentinel = object()
        missing = object()
        module_names = ("fla", "causal_conv1d")
        previous_modules = {
            name: sys.modules.get(name, missing) for name in module_names
        }

        def verify_cpu_runtime(*args: object, **kwargs: object) -> Mock:
            self.assertEqual(os.environ["THX02_DEVICE"], "cpu")
            self.assertIsNone(sys.modules["fla"])
            self.assertIsNone(sys.modules["causal_conv1d"])
            return Mock()

        try:
            for name in module_names:
                sys.modules[name] = sentinel
            with (
                patch.dict(os.environ, {"THX02_DEVICE": "cuda"}),
                patch("huggingface_hub.snapshot_download", return_value="/tmp/thx02-cache"),
                patch("thx02.THX02.load", side_effect=verify_cpu_runtime) as load,
                contextlib.redirect_stderr(io.StringIO()),
            ):
                _load_model("cpu")
                load.assert_called_once_with("/tmp/thx02-cache", device="cpu")
        finally:
            for name, previous in previous_modules.items():
                if previous is missing:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = previous


    def test_model_load_downloads_when_cache_is_missing(self) -> None:
        """A missing cache triggers one download and loads the downloaded path."""
        from huggingface_hub.errors import LocalEntryNotFoundError

        downloaded_path = "/tmp/thx02-downloaded"
        with (
            patch(
                "huggingface_hub.snapshot_download",
                side_effect=[LocalEntryNotFoundError("missing"), downloaded_path],
            ) as download,
            patch("thx02.THX02.load", return_value=Mock()) as load,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            _load_model("cpu")

        self.assertEqual(download.call_count, 2)
        self.assertTrue(download.call_args_list[0].kwargs["local_files_only"])
        self.assertNotIn("local_files_only", download.call_args_list[1].kwargs)
        load.assert_called_once_with(downloaded_path, device="cpu")


if __name__ == "__main__":
    unittest.main()
