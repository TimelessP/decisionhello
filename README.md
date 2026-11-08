# decisionhello

A small command-line playground for trying [HAL-X-AI/THX-02](https://huggingface.co/HAL-X-AI/THX-02), a model that answers typed decision questions about text and images. The demos include support-ticket triage, a chart, a spreadsheet, and object classification.

## Get started

You need Python 3.12 and an internet connection to call the THX-02 API.

```bash
git clone https://github.com/TimelessP/decisionhello.git
cd decisionhello
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

In PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

The HAL-X API key is optional on its free tier (which may be rate-limited by IP). If you have a key, set it in your shell; do not put it in source files:

```bash
export HALX_API_KEY="your-key"
```

```powershell
$env:HALX_API_KEY = "your-key"
```

Run the first text demo:

```bash
python -m decisionhello demo --scenario support
```

The response contains the selected answer and probabilities. For example, support triage returns a suggested team, urgency, and whether the customer asks for a refund. Answers are model predictions, not guaranteed facts.

## Try the image demos

Each command sends one example image and its question to THX-02:

```bash
python -m decisionhello demo --scenario chart
python -m decisionhello demo --scenario spreadsheet
python -m decisionhello demo --scenario dog
python -m decisionhello demo --scenario bicycle
python -m decisionhello demo --scenario mug
```

The chart asks which quarter has the most units sold; the spreadsheet asks which product has the highest sales count. The other images ask the model to identify the pictured object.

| Chart | Spreadsheet |
|---|---|
| ![Quarterly sales chart](examples/images/chart.png) | ![Store sales spreadsheet](examples/images/spreadsheet.png) |

Object examples: [dog](examples/images/dog.png), [bicycle](examples/images/bicycle.png), [mug](examples/images/mug.png).

To run every included demo in sequence (six API requests):

```bash
python -m decisionhello demo --scenario all --think auto
```

`--think` accepts `false`, `auto`, or `true`; it defaults to `auto`. Thinking can add latency. Select a single scenario while exploring to avoid making unnecessary API requests.

## Classify your own image

Pass a local image path and a comma-separated set of candidate labels:

```bash
python -m decisionhello classify path/to/photo.png
python -m decisionhello classify path/to/photo.png --labels "dog,cat,wolf,other"
python -m decisionhello classify path/to/photo.png --question "Which vehicle is shown?"
```

The default labels are `dog,bicycle,mug,chart,spreadsheet,other`. The app sends the image to the THX-02 API; do not use it with private or sensitive images unless you are comfortable with the service's data handling.

## Regenerate example images

Five synthetic sample images are checked in under `examples/images/`. They are generated locally with Pillow and do not require a separate image-generation service:

```bash
python scripts/create_examples.py
```

## Other useful commands

```bash
python -m decisionhello --help
python -m decisionhello demo --help
python -m unittest discover -s tests -v
```

## How it works

`thx02` is the official Python API client. The app supplies a state, one or more typed questions, and optionally an image path; the service returns answers and probability distributions. The example image generator uses Pillow. Dependency versions are pinned in `requirements.txt`.

The THX-02 model and API are provided by HAL-X and are separate from this MIT-licensed example application. See the [model card](https://huggingface.co/HAL-X-AI/THX-02) and [API documentation](https://api.hal-x.ai/docs/thx-02/) for model terms, service details, and limitations. This toy app is for experimentation, not consequential decisions.
