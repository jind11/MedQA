"""word vector similarity solver"""

import argparse

from aristomini.common.solver import SolverBase
from aristomini.common.models import MultipleChoiceQuestion, MultipleChoiceAnswer, ChoiceConfidence
from aristomini.common.wordtwovec import WordTwoVec

parser = argparse.ArgumentParser()
parser.add_argument("model_file")


class WordVectorSimilaritySolver(SolverBase):
    """uses word2vec to score questions"""
    def __init__(self, model_file: str) -> None:
        self.word_two_vec = WordTwoVec(model_file)

    def solver_info(self) -> str:
        return "word_vector_similarity"

    def answer_question(self, question: MultipleChoiceQuestion) -> MultipleChoiceAnswer:
        mca = MultipleChoiceAnswer(
            [ChoiceConfidence(choice, self.word_two_vec.goodness(question.stem, choice.text))
             for choice in question.choices]
        )

        return mca

if __name__ == "__main__":
    args = parser.parse_args()
    solver = WordVectorSimilaritySolver(args.model_file)
    solver.run()
