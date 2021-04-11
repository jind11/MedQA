"""text search solver"""
import argparse
import jsonlines

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Search

import sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from aristomini.common.solver import SolverBase
from aristomini.common.models import MultipleChoiceQuestion, MultipleChoiceAnswerwithContext, ChoiceConfidenceContext

def char2num(char):
    return ord(char) - ord('A')

def num2char(num):
    return chr(ord('A') + num)

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

    def score(self, question_stem: str, choice_text: str):
        """get the score from elasticsearch"""
        query_text = "{0} {1}".format(question_stem, choice_text)
        query = Q('multi_match', query=query_text, fields=self.fields)
        search = Search(using=self.client, index=self.index_name).query(query)[:self.topn]
        response = search.execute()
        return sum(hit.meta.score for hit in response), \
               [self.client.get(index=self.index_name, doc_type='sentence', id=hit.meta.id)["_source"][self.fields[0]] for hit in response]

    def solver_info(self) -> str:
        return "text_search"

    def answer_question(self, question: MultipleChoiceQuestion) -> MultipleChoiceAnswerwithContext:
        return MultipleChoiceAnswerwithContext(
            [ChoiceConfidenceContext(choice, *self.score(question.stem, choice.text))
             for choice in question.choices]
        )


def answer_to_selection(answer: MultipleChoiceAnswerwithContext):
    choices = answer.choiceConfidences
    max_confidence = 0
    best_choice = None
    for choice in choices:
        if choice.confidence > max_confidence:
            max_confidence = choice.confidence
            best_choice = choice

    return best_choice


def extract_answers(solver, data_path, out_path):
    answers = []
    best_choices = []
    num_corrects = 0
    with open(data_path, 'r') as f, open(out_path+'.txt', 'w') as ofile_txt, \
            jsonlines.open(out_path+'.jsonl', 'w') as ofile_jsonl:
        for idx, line in enumerate(f):
            question = MultipleChoiceQuestion.from_jsonl_ours(line, idx)
            answer = solver.answer_question(question)
            answers.append(answer)
            best_choice = answer_to_selection(answer)
            if best_choice.choice.label == question.answerKey:
                num_corrects += 1
            if idx > 1 and idx % 200 == 0:
                print('{} finished!'.format(idx))

            # here we want to write the log file in txt format
            ofile_txt.write('-' * 15 + 'Question' + '-' * 15 + '\n')
            ofile_txt.write('{}\n'.format(question.stem))
            ofile_txt.write('-' * 15 + 'Answers' + '-' * 15 + '\n')
            choice_confidence = {choice.choice.label: choice.confidence for choice in answer.choiceConfidences}
            choice_context = {choice.choice.label: choice.context for choice in answer.choiceConfidences}
            for choice in question.choices:
                ofile_txt.write('Ground True: {}\tIR confidence: {}\tAnswer Text: {}\n'
                            .format('Right' if choice.label == question.answerKey else 'Wrong',
                                    choice_confidence[choice.label],
                                    choice.text))
            ofile_txt.write('-' * 15 + 'IR retrieved results' + '-' * 15 + '\n')
            for choice in question.choices:
                if choice.label == question.answerKey:
                    ofile_txt.write('-' * 15 + '{} Answer: {}'.format('Right' if choice.label == question.answerKey else 'Wrong',
                                                                  choice.text) + '-' * 15 + '\n')
                    for k, hit in enumerate(choice_context[choice.label]):
                        ofile_txt.write('-' * 15 + 'Hit {}\n'.format(k))
                        ofile_txt.write('{}'.format(hit))
                # ofile.write('\n')
            ofile_txt.write('\n\n')

            # here we want to write the log file in jsonl format
            tmp = {}
            contexts = []
            options = []
            for ii in range(len(choice_confidence)):
                contexts.append(choice_context[num2char(ii)])
                options.append(question.choices[ii].text)
            tmp['contexts'] = contexts
            tmp['options'] = options
            tmp['question'] = question.stem
            tmp['answer_idx'] = char2num(question.answerKey)
            ofile_jsonl.write(tmp)

            # if idx > 10:
            #     exit(0)

    print('accuracy is: {} / {} = {:.1f}%'.format(num_corrects, len(answers), num_corrects * 100.0 / len(answers)))
    return answers, best_choices


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True, help='path of data we want to get answers for')
    parser.add_argument('--out_path', type=str, required=True, help='path of file to write query results')
    args = parser.parse_args()

    # create the text search solver
    solver = TextSearchSolver(topn=30)  # pylint: disable=invalid-name

    # read the question data and get the answers to them using the solver
    answers = extract_answers(solver, args.data_path, args.out_path)
