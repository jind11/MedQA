"""base class that solvers should inherit from"""

from typing import Any

from aristomini.common.models import MultipleChoiceQuestion, MultipleChoiceAnswer, \
    SolverAnswer, parse_question

# built in `json` module doesn't serialize namedtuples correctly; `simplejson` does.
import simplejson as json
from flask import Flask, request
from flask_cors import CORS

class SolverBase:
    """
    interface for solvers. to implement one just inherit from this class and override
    `answer_question` and `solver_info`
    """
    def run(self, host='localhost', port=8000) -> None:
        """run the solver"""
        app = Flask(__name__)
        CORS(app)

        @app.route('/answer', methods=['GET', 'POST'])
        def solve() -> Any:  # pylint: disable=unused-variable
            """
            get a json-serialized MultipleChoiceQuestion out of the request body, feed it to
            answer_question, and return the json-serialized result
            """
            body = request.get_json(force=True)
            question = parse_question(body)
            multiple_choice_answer = self.answer_question(question)
            solver_answer = SolverAnswer(solverInfo=self.solver_info(),
                                         multipleChoiceAnswer=multiple_choice_answer)
            return json.dumps(solver_answer)

        @app.route('/solver-info')
        def info():  # pylint: disable=unused-variable
            """return the solver name"""
            return self.solver_info()

        app.run(host=host, port=port)

    def answer_question(self, question: MultipleChoiceQuestion) -> MultipleChoiceAnswer:
        """answer the question"""
        raise NotImplementedError()

    def solver_info(self) -> str:
        """info about the solver"""
        raise NotImplementedError()
