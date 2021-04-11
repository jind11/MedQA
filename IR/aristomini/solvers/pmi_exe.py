import requests
import argparse
from aristomini.common.models import MultipleChoiceQuestion, MultipleChoiceAnswer, ChoiceConfidence


def answer_to_selection(answer):
    choices = answer["choiceConfidences"]
    max_confidence = -1e6
    best_choice = None
    for choice in choices:
        if choice["confidence"] > max_confidence:
            max_confidence = choice["confidence"]
            best_choice = choice

    return best_choice


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True, help='path of data we want to get answers for')
    args = parser.parse_args()

    answers = []
    best_choices = []
    num_corrects = 0
    with open(args.data_path, 'r') as f:
        for idx, line in enumerate(f):
            question = MultipleChoiceQuestion.from_jsonl_ours(line, idx)
            r = requests.post('http://localhost:9000/answer', json=question)
            answer = r.json()["multipleChoiceAnswer"]
            best_choice = answer_to_selection(answer)
            answers.append(answer)
            best_choices.append(best_choice)
            if best_choice["choice"]["label"] == question.answerKey:
                num_corrects += 1
            if idx > 1 and idx % 200 == 0:
                print("{} finished!".format(idx))

    print('accuracy is: {} / {} = {:.1f}%'.format(num_corrects, len(answers), num_corrects * 100.0 / len(answers)))