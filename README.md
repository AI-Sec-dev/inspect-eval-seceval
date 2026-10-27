# SecEval Benchmark

An [Inspect AI](https://inspect.aisi.org.uk/) implementation of
[SecEval](https://xuanwuai.github.io/SecEval/), a benchmark for evaluating the
cybersecurity knowledge of language models.

The bundled dataset contains 2,189 questions with four answer options each.
Questions may have one or multiple correct answers. The evaluation uses
Inspect's `multiple_choice(multiple_correct=True)` solver and `choice()` scorer
to report accuracy. Responses should use `ANSWER: B` for a single answer or
`ANSWER: A,C` for multiple answers. All correct options must be selected;
partially correct selections receive no credit.

The system prompt is: `You are a security expert who answers questions.`

The dataset is bundled in `src/seceval/dataset/seceval_dataset.json`. If it is
missing, the loader downloads `questions.json` from the
[upstream Hugging Face dataset](https://huggingface.co/datasets/XuanwuAI/SecEval/tree/205dab7b0888a06f4b53ca7d9c7093e1326683e1),
pinned to revision `205dab7b0888a06f4b53ca7d9c7093e1326683e1`, verifies its
SHA-256 checksum, and saves a local copy. Original sample IDs and answer keys
are preserved.

**Dataset limitation:** Seven bundled records have empty answer fields. The
current loader includes these records without filtering or repairing their
answer keys; account for this when interpreting aggregate accuracy.

## Installation

Python 3.11 or newer is required. Clone the repository and install the project
with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/AI-Sec-dev/inspect-eval-seceval.git
cd inspect-eval-seceval
uv sync
```

## Usage

Set the credentials required by your model provider, then run:

```bash
uv run inspect eval seceval/seceval --model <provider/model>

# Limit the evaluation to ten samples
uv run inspect eval seceval/seceval --model <provider/model> --limit 10

# Evaluate a specific sample using its original ID
uv run inspect eval seceval/seceval --model <provider/model> --sample-id 282cd7f6-86f9-4174-95c2-df26b2b6395e
```

For example, run a smoke test with a mock model without model API credentials:

```bash
uv run inspect eval seceval/seceval --model mockllm/model --limit 10
```

Mock-model results check execution only; they do not measure model capability.
The first run may download tokenizer data. Inspect saves evaluation logs under
`logs/` by default. View them with:

```bash
uv run inspect view
```

## Development

```bash
uv sync
uv run pytest tests/test_seceval.py
uv run ruff check
uv run ruff format --check
```

The tests cover sample conversion, local dataset loading, reuse of an existing
dataset without downloading, download fallback with a mocked downloader, and
correct and incorrect single- and multiple-answer responses through the real
solver and scorer with a mock model. They also check that the system prompt is
included.

## Citation

If you use this evaluation, cite the original
[SecEval benchmark](https://xuanwuai.github.io/SecEval/#citation):

```bibtex
@misc{li2023seceval,
  title = {SecEval: A Comprehensive Benchmark for Evaluating Cybersecurity Knowledge of Foundation Models},
  author = {Li, Guancheng and Li, Yifeng and Wang, Guannan and Yang, Haoyu and Yu, Yang},
  publisher = {GitHub},
  howpublished = {https://github.com/XuanwuAI/SecEval},
  year = {2023}
}
```

## License

This implementation is licensed under the [MIT License](LICENSE). The dataset
is distributed separately under CC BY-NC-SA (Attribution-NonCommercial-ShareAlike),
as stated on the [SecEval project website](https://xuanwuai.github.io/SecEval/).
