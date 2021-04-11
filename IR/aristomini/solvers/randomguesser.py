"""random guesser solver"""

import random

from aristomini.common.solver import SolverBase
from aristomini.common.models import MultipleChoiceQuestion, MultipleChoiceAnswer, ChoiceConfidence


class RandomGuesserSolver(SolverBase):
    """guesses at random"""
    def solver_info(self) -> str:
        return "random_guesser"

    def answer_question(self, question: MultipleChoiceQuestion) -> MultipleChoiceAnswer:
        return MultipleChoiceAnswer(
            [ChoiceConfidence(choice, random.random()) for choice in question.choices]
        )

if __name__ == "__main__":
    solver = RandomGuesserSolver()  # pylint: disable=invalid-name
    solver.run()
