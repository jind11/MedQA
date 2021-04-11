"""pmi solver"""

from collections import defaultdict
import math
from typing import NamedTuple, Iterable, List, Dict, Set, Sequence

from aristomini.common.solver import SolverBase
from aristomini.common.models import MultipleChoiceQuestion, MultipleChoiceAnswer, ChoiceConfidence
from aristomini.common.nlp import all_grams, distinct_grams, get_sentences, stemmer

SOME_SMALL_DEFAULT_VALUE = 0.01

def pmi(prob_x: float, prob_y: float, prob_xy: float) -> float:
    """calculate pmi using probabilities, return 0.0 if p_xy is 0"""
    if prob_xy > 0.0:
        return math.log(prob_xy / prob_x / prob_y)
    else:
        return 0.0

SentenceConcepts = NamedTuple("SentenceConcepts",
                              [("grams", List[str]), ("concepts", Set[int])])

class AcmeScorer:
    """keeps all the indexes in memory"""
    def __init__(self,
                 concept_sentences: Iterable[SentenceConcepts],
                 concepts: Sequence[str],
                 min_sentences: int=100,
                 stem: bool=True) -> None:
        """init"""
        self.concepts = concepts
        self.num_sentences = 0
        self.gram_counts = defaultdict(int) # type: Dict[str, int]
        self.concept_counts = defaultdict(int) # type: Dict[int, int]
        # gram -> concept -> count
        self.gram_concept_counts = defaultdict(lambda: defaultdict(int)) # type: Dict[str, Dict[int, int]]

        for i, sc in enumerate(concept_sentences):
            self.num_sentences += 1

            for concept in sc.concepts:
                self.concept_counts[concept] += 1

            #grams = distinct_grams(all_grams(sc.sentence, stem))
            grams = sc.grams
            for gram in grams:
                self.gram_counts[gram] += 1

                for concept in sc.concepts:
                    self.gram_concept_counts[gram][concept] += 1

            if i % 1000 == 0:
                print("indexing {}".format(i))

        self.concept_counts = {
            concept: count
            for concept, count in self.concept_counts.items()
            if count >= min_sentences
        }

    def pmi(self, gram: str, concept: int) -> float:
        """pmi"""
        n_gram = self.gram_counts[gram]
        n_concept = self.concept_counts[concept]
        n_gram_concept = self.gram_concept_counts[gram][concept]

        p_gram = n_gram / self.num_sentences
        p_gram_given_concept = n_gram_concept / n_concept

        if p_gram_given_concept > 0:
            return math.log(p_gram_given_concept / p_gram)
        else:
            return SOME_SMALL_DEFAULT_VALUE

    def average_pmi(self, grams: Sequence[str], concept: int) -> float:
        """average pmi"""
        pmis = [self.pmi(gram, concept) for gram in grams]
        if not pmis:
            return 0.0
        else:
            return sum(pmis) / len(pmis)


    def score(self,
              question: MultipleChoiceQuestion,
              stem: bool=True,
              topn: int=1) -> MultipleChoiceAnswer:
        """calculate the scores"""
        question_text = question.stem
        verbose = "Max is doing" in question_text

        results = []
        for choice in question.choices:
            grams = distinct_grams(all_grams(question_text + " " + choice.text))

            # get the relevant concepts
            concepts = {
                concept
                for gram in grams
                for concept in self.gram_concept_counts[gram]
                if concept in self.concept_counts
            }

            concept_scores = sorted([
                (concept, self.average_pmi(grams, concept))
                for concept in concepts
            ], key=lambda pair: pair[-1], reverse=True)

            results.append(sum(s for _, s in concept_scores[:topn]))

            if verbose:
                print(choice.text)
                for concept, score in concept_scores:
                    print(self.concepts[concept], score)
                print()

        return MultipleChoiceAnswer(
            [ChoiceConfidence(choice, pmi)
             for choice, pmi in zip(question.choices, results)]
        )



class AcmeSolver(SolverBase):
    """uses pmi"""
    def __init__(self,
                 sentences: Iterable[str],
                 concepts: Iterable[str]) -> None:
        print("creating scorer")

        cs = []

        concepts = list({
            stemmer(concept) for concept in concepts
        })

        concept_index = { concept: i for i, concept in enumerate(concepts)}

        for sentence in sentences:
            cis = set()  # type: Set[int]
            grams = distinct_grams(all_grams(sentence))

            for gram in grams:
                ci = concept_index.get(gram)
                if ci is not None:
                    cis.add(ci)

            cs.append(SentenceConcepts(grams, cis))

            if len(cs) % 1000 == 0:
                print(len(cs))

        self.scorer = AcmeScorer(cs, concepts)
        print("loaded scorer")

    def solver_info(self) -> str:
        return "acme"

    def answer_question(self, question: MultipleChoiceQuestion) -> MultipleChoiceAnswer:
        return self.scorer.score(question)

if __name__ == "__main__":
    print("loading concepts")
    concepts = get_sentences("concepts.txt")
    print("loaded {} concepts".format(len(concepts)))
    print("loading sentences")
    sentences = get_sentences('aristo-mini-corpus-v1.txt')
    print("loaded {} sentences".format(len(sentences)))
    solver = AcmeSolver(sentences, concepts)
    solver.run()
