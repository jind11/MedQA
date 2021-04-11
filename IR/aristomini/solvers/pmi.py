"""pmi solver"""

from collections import defaultdict
import math
from typing import NamedTuple, Iterable, List, Dict

from aristomini.common.solver import SolverBase
from aristomini.common.models import MultipleChoiceQuestion, MultipleChoiceAnswer, ChoiceConfidence
from aristomini.common.nlp import all_grams, distinct_grams, get_sentences


def pmi(prob_x: float, prob_y: float, prob_xy: float) -> float:
    """calculate pmi using probabilities, return 0.0 if p_xy is 0"""
    if prob_xy > 0.0:
        return math.log(prob_xy / prob_x / prob_y)
    else:
        return 0.0


class PmiScorer:
    """keeps all the indexes in memory"""
    def __init__(self,
                 sentences: Iterable[str],
                 stem: bool=True,
                 within: int=10) -> None:
        """init"""
        self.num_sentences = 0
        self.index = defaultdict(lambda: defaultdict(list))  # type: Dict[str, Dict[int, List[int]]]
        for i, sentence in enumerate(sentences):
            self.num_sentences += 1
            for gram in all_grams(sentence):
                self.index[gram.gram][i].append(gram.position)
            if i % 1000 == 0:
                print("indexing {}".format(i))

        print("grams {}".format(len(self.index)))

        self.within = within

    def num_occurrences(self, gram: str) -> int:
        """get the number of sentences in which a gram appears"""
        return len(self.index.get(gram, {}))

    def num_co_occurrences(self, gram1: str, gram2: str) -> int:
        """get the number of sentences in which two grams occur closely"""

        index1 = self.index.get(gram1, {})
        index2 = self.index.get(gram2, {})

        return len([
            sentence
            for sentence, locs in index1.items()
            if any(abs(loc1-loc2) <= self.within
                   for loc1 in locs
                   for loc2 in index2.get(sentence, []))
        ])


    def count_pmi(self, num_x: int, num_y: int, num_xy: int) -> float:
        """calculate pmi using counts"""

        return pmi(num_x / self.num_sentences,
                   num_y / self.num_sentences,
                   num_xy / self.num_sentences)

    def score(self, question: MultipleChoiceQuestion, stem: bool=False) -> MultipleChoiceAnswer:
        """calculate the scores"""
        question_text = question.stem
        verbose = "Max is doing" in question_text

        # compute these outside the for loop so they only get computed once
        q_grams = distinct_grams(all_grams(question_text))
        q_counts = [self.num_occurrences(gram) for gram in q_grams]

        results = []
        for choice in question.choices:
            answer = choice.text
            if verbose: print(answer)
            total_pmi = 0.0
            count = 0
            for a_gram in distinct_grams(all_grams(answer)):
                a_count = self.num_occurrences(a_gram)
                for q_gram, q_count in zip(q_grams, q_counts):
                    co_count = self.num_co_occurrences(q_gram, a_gram)
                    cpmi = self.count_pmi(q_count, a_count, co_count)
                    total_pmi += cpmi
                    count += 1
                    if verbose and cpmi > 0:
                        print(q_gram, "/", a_gram, "/", q_count, a_count, co_count, cpmi)
            if verbose:
                print(total_pmi, count, total_pmi / count)
            if count > 0:
                results.append(total_pmi / count)
            else:
                results.append(0)

        return MultipleChoiceAnswer(
            [ChoiceConfidence(choice, pmi)
             for choice, pmi in zip(question.choices, results)]
        )


class PmiSolver(SolverBase):
    """uses pmi"""
    def __init__(self, sentences: Iterable[str]) -> None:
        print("creating scorer")
        self.scorer = PmiScorer(sentences)
        print("loaded scorer")

    def solver_info(self) -> str:
        return "pmi"

    def answer_question(self, question: MultipleChoiceQuestion) -> MultipleChoiceAnswer:
        return self.scorer.score(question)

if __name__ == "__main__":
    print("loading sentences")
    sentences = get_sentences('/data/medg/misc/jindi/nlp/datasets/MedQA/textbooks/zh_sentence/all_books.txt')
    print("loaded {} sentences".format(len(sentences)))
    solver = PmiSolver(sentences)
    solver.run(port=9000)
