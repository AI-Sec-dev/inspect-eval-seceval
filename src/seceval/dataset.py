"""Dataset loading and sample adapter for the SecEval benchmark."""

from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
from typing import Any

from inspect_ai.dataset import Dataset, Sample, json_dataset
from inspect_ai.util import download

DATASET_FILE = Path(__file__).parent / "dataset" / "seceval_dataset.json"
DATASET_REVISION = "205dab7b0888a06f4b53ca7d9c7093e1326683e1"
DATASET_URL = (
    "https://huggingface.co/datasets/XuanwuAI/SecEval/resolve/"
    f"{DATASET_REVISION}/questions.json"
)
DATASET_SHA256 = "194c3a511104be422a678675a71d44315d0c0392b040745155aeebc321e692e0"


def _ensure_dataset_file(json_file: Path = DATASET_FILE) -> Path:
    """Download the upstream dataset when the local JSON file is absent."""
    if json_file.is_file():
        return json_file

    with TemporaryDirectory() as temp_dir:
        downloaded_file = download(
            DATASET_URL,
            DATASET_SHA256,
            Path(temp_dir) / "questions.json",
        )
        json_file.parent.mkdir(parents=True, exist_ok=True)
        copyfile(downloaded_file, json_file)
    return json_file


def load_dataset() -> Dataset:
    """Load the SecEval JSON dataset using its existing sample IDs."""
    return json_dataset(
        json_file=str(_ensure_dataset_file()),
        sample_fields=record_to_sample,
    )


def record_to_sample(record: dict[str, Any]) -> Sample:
    """Convert a SecEval record into an Inspect sample."""
    return Sample(
        id=record["id"],
        input=str(record["question"]) + "\n" + str(record["choices"]),
        choices=["A", "B", "C", "D"],
        target=record["answer"],
    )
