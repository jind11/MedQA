"""
typed models for our data. these are the exact analogues of the case classes used by the scala
code (which is why the fields have unfortunate, non-pythonic names)
"""
from typing import NamedTuple, List, Any, Dict, NamedTuple

import simplejson as json

# pylint: disable=invalid-name

def num2char(num):
    return chr(ord('A') + num)

class Choice(NamedTuple):
    label: str
    text: str

class ChoiceConfidence(NamedTuple):
    choice: Choice
    confidence: float

class ChoiceConfidenceContext(NamedTuple):
    choice: Choice
    confidence: float
    context: str

class MultipleChoiceAnswer(NamedTuple):
    choiceConfidences: List[ChoiceConfidence]

class MultipleChoiceAnswerwithContext(NamedTuple):
    choiceConfidences: List[ChoiceConfidenceContext]

class SolverAnswer(NamedTuple):
    solverInfo: str
    multipleChoiceAnswer: MultipleChoiceAnswer

class MultipleChoiceQuestion(NamedTuple):
    stem: str
    choices: List[Choice]
    id_: str = None
    answerKey: str = None

    @staticmethod
    def from_jsonl(line: str) -> 'MultipleChoiceQuestion':
        blob = json.loads(line)
        question = blob['question']
        return MultipleChoiceQuestion(
            id_=blob['id'],
            stem=question['stem'],
            choices=[Choice(c["label"], c["text"]) for c in question['choices']],
            answerKey=blob['answerKey'],
        )

    @staticmethod
    def from_jsonl_ours(line: str, idx: int) -> 'MultipleChoiceQuestion':
        blob = json.loads(line)
        return MultipleChoiceQuestion(
            id_=idx,
            stem=blob['question'],
            choices=[Choice(num2char(idx), blob['options'][num2char(idx)]) for idx in range(len(blob['options']))],
            answerKey=blob['answer_idx'],
        )

class Exam(NamedTuple):
    name: str
    questions: List[MultipleChoiceQuestion]

def parse_question(blob: Dict[str, Any]) -> MultipleChoiceQuestion:
    """parses a question from a json blob. is possibly too lenient to malformed json"""
    return MultipleChoiceQuestion(
        stem=blob.get("stem", ""),
        choices=[Choice(c["label"], c["text"]) for c in blob.get("choices", [])]
    )
