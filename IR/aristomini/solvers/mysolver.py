"""
This is a skeleton for building your own solver.

You just need to find and fix the two TODOs in this file.
"""
from typing import List

from aristomini.common.solver import SolverBase
from aristomini.common.models import MultipleChoiceQuestion, MultipleChoiceAnswer, ChoiceConfidence

# TODO: replace with your solver name.
MY_SOLVER_NAME = "replace me with the name of your solver"

class MySolver(SolverBase):
    def solver_info(self) -> str:
        return MY_SOLVER_NAME

    def answer_question(self, question: MultipleChoiceQuestion) -> MultipleChoiceAnswer:
        # pylint: disable=unused-variable

        stem = question.stem
        choices = question.choices

        confidences: List[float] = []

        for i, choice in enumerate(question.choices):
            label = choice.label
            text = choice.text

            # TODO: compute confidence
            confidence = 0

            confidences.append(confidence)

        return MultipleChoiceAnswer(
            [ChoiceConfidence(choice, confidence)
             for choice, confidence in zip(choices, confidences)]
        )

if __name__ == "__main__":
    solver = MySolver()  # pylint: disable=invalid-name
    solver.run()
