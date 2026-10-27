"""Inspect task definition for the SecEval benchmark (https://xuanwuai.github.io/SecEval/)."""

from inspect_ai import Task, task
from inspect_ai.scorer import choice
from inspect_ai.solver import multiple_choice, system_message

from .dataset import load_dataset

SYSTEM_MESSAGE = "You are a security expert who answers questions."


@task
def seceval() -> Task:
    """Task to evaluate the cybersecurity knowledge of LLMs using multiple choice questions. Several answers may be correct."""
    return Task(
        dataset=load_dataset(),
        solver=[system_message(SYSTEM_MESSAGE), multiple_choice(multiple_correct=True)],
        scorer=choice(),
    )
