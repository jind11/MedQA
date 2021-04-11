"""text search solver"""
import argparse

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Search

from aristomini.common.solver import SolverBase
from aristomini.common.models import MultipleChoiceQuestion, MultipleChoiceAnswer, ChoiceConfidence


class TextSearchSolver(object):
    """
    runs a query against elasticsearch and sums up the top `topn` scores. by default,
    `topn` is 1, which means it just returns the top score, which is the same behavior as the
    scala solver
    """
    def __init__(self,                   # pylint: disable=too-many-arguments
                 host: str="localhost",
                 port: int=9200,
                 index_name: str="knowledge",
                 field_name: str="body",
                 topn: int=1) -> None:
        self.client = Elasticsearch([host], port=port)
        print(self.client)
        self.fields = [field_name]
        self.index_name = index_name
        self.topn = topn

    def score(self, question_stem: str, choice_text: str) -> float:
        """get the score from elasticsearch"""
        query_text = "{0} {1}".format(question_stem, choice_text)
        query = Q('multi_match', query=query_text, fields=self.fields)
        search = Search(using=self.client, index=self.index_name).query(query)[:self.topn]
        response = search.execute()
        return sum(hit.meta.score for hit in response)

    def solver_info(self) -> str:
        return "text_search"

    def answer_question(self, question: MultipleChoiceQuestion) -> MultipleChoiceAnswer:
        return MultipleChoiceAnswer(
            [ChoiceConfidence(choice, self.score(question.stem, choice.text))
             for choice in question.choices]
        )


def answer_to_selection(answer: MultipleChoiceAnswer):
    choices = answer.choiceConfidences
    max_confidence = 0
    best_choice = None
    for choice in choices:
        if choice.confidence > max_confidence:
            max_confidence = choice.confidence
            best_choice = choice

    return best_choice


def extract_answers(solver, data_path):
    answers = []
    best_choices = []
    num_corrects = 0
    with open(data_path, 'r') as f:
        for idx, line in enumerate(f):
            question = MultipleChoiceQuestion.from_jsonl_ours(line, idx)
            answer = solver.answer_question(question)
            answers.append(answer)
            best_choice = answer_to_selection(answer)
            if best_choice.choice.label == question.answerKey:
                num_corrects += 1
            # if idx % 200 == 0:
            #     print('{} finished!'.format(idx))
    print('accuracy is: {} / {} = {:.1f}%'.format(num_corrects, len(answers), num_corrects * 100.0 / len(answers)))
    return answers, best_choices


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True, help='path of data we want to get answers for')
    parser.add_argument('--topn', type=int, default=1, help='number of IR results selected')
    args = parser.parse_args()

    # create the text search solver
    for topn in [args.topn]:
        print('topn: {}'.format(topn))
        solver = TextSearchSolver(topn=topn)  # pylint: disable=invalid-name

        # read the question data and get the answers to them using the solver
        answers = extract_answers(solver, args.data_path)
