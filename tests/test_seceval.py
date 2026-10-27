"""Tests for the SecEval dataset and multiple-choice evaluation."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from inspect_ai import eval
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import ModelOutput, get_model

from seceval.dataset import (
    DATASET_FILE,
    _ensure_dataset_file,
    load_dataset,
    record_to_sample,
)
from seceval.seceval import SYSTEM_MESSAGE, seceval


@pytest.mark.parametrize("answer", ["B", "AC", "ABCD"])
def test_record_to_sample(answer: str) -> None:
    record = {
        "id": "security-1",
        "question": "Which options are secure?",
        "choices": ["A: First", "B: Second", "C: Third", "D: Fourth"],
        "answer": answer,
    }

    sample = record_to_sample(record)

    assert sample.id == record["id"]
    assert sample.input == f"{record['question']}\n{record['choices']}"
    assert sample.choices == ["A", "B", "C", "D"]
    assert sample.target == answer


def test_load_dataset() -> None:
    records = json.loads(DATASET_FILE.read_text(encoding="utf-8"))
    dataset = load_dataset()

    assert len(dataset) == len(records) > 0
    assert len({sample.id for sample in dataset}) == len(dataset)
    for sample, record in zip(dataset, records, strict=True):
        assert sample.id == record["id"]
        assert sample.target == record["answer"]
        assert sample.choices == ["A", "B", "C", "D"]


def test_existing_dataset_does_not_download(tmp_path: Path) -> None:
    cached = tmp_path / "questions.json"
    cached.write_text("[]", encoding="utf-8")

    with patch("seceval.dataset.download") as download:
        assert _ensure_dataset_file(cached) == cached

    download.assert_not_called()
    assert cached.read_text(encoding="utf-8") == "[]"


def test_missing_dataset_is_downloaded(tmp_path: Path) -> None:
    source = tmp_path / "download.json"
    source.write_text('[{"id": "example"}]', encoding="utf-8")
    destination = tmp_path / "dataset" / "questions.json"

    with patch("seceval.dataset.download", return_value=source) as download:
        assert _ensure_dataset_file(destination) == destination

    download.assert_called_once()
    assert destination.read_bytes() == source.read_bytes()


@pytest.mark.parametrize(
    ("target", "answer", "expected_score"),
    [("B", "B", "C"), ("B", "A", "I"), ("AC", "A,C", "C"), ("AC", "A", "I")],
)
def test_seceval_scoring(
    tmp_path: Path, target: str, answer: str, expected_score: str
) -> None:
    dataset = MemoryDataset(
        [
            Sample(
                id="security-1",
                input="Select the secure options.",
                choices=["A", "B", "C", "D"],
                target=target,
            )
        ]
    )
    with patch("seceval.seceval.load_dataset", return_value=dataset):
        task = seceval()

    [log] = eval(
        tasks=task,
        model=get_model(
            "mockllm/model",
            custom_outputs=[
                ModelOutput.from_content("mockllm/model", f"ANSWER: {answer}")
            ],
        ),
        log_dir=str(tmp_path / "logs"),
        display="none",
    )

    assert log.status == "success", log.error
    assert log.samples is not None
    assert len(log.samples) == 1
    sample = log.samples[0]
    assert sample.scores is not None
    assert sample.scores["choice"].value == expected_score
    assert any(
        message.role == "system" and message.content == SYSTEM_MESSAGE
        for message in sample.messages
    )
