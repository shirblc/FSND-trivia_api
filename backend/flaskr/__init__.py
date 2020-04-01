import os
import json
import sys
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # Adding CORS response headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST,\
         DELETE')
        return response

    # Function to paginate the questions and return them as a list
    def paginate_questions(questions, current_page):
        # Gets the number of the first question in the page and the relevant
        # questions from the list passed to the function.
        first_question_num = QUESTIONS_PER_PAGE * (current_page - 1)
        paginated_questions = questions[first_question_num:
                                        (first_question_num+10)]
        paginated_questions_list = []

        # For every question in the list, formats it and adds to formatted list
        for question in paginated_questions:
            paginated_questions_list.append(question.format())

        return paginated_questions_list

    # Route Handlers
    # -------------------------------------------------------

    # Home route handler.
    @app.route('/')
    def index():
        return redirect(url_for('load_questions'))

    # Route handler for the questions page. Redirected from the home page.
    @app.route('/questions')
    def load_questions():
        # Gets the questions, categories and current page. Gets paginated
        # Questions by sending the questions to the paginate function.
        questions = Question.query.order_by(Question.id).all()
        current_page = request.args.get('page', 1, type=int)
        paginated_questions_list = paginate_questions(questions, current_page)
        categories = Category.query.all()
        categories_dict = {}

        # Creates a dictionary from all category objects.
        for category in categories:
            categories_dict[category.id] = category.type

        # If there are no questions, the page is out of bounds.
        if(len(paginated_questions_list) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'current_page': current_page,
            'questions': paginated_questions_list,
            'total_questions': len(questions),
            'categories': categories_dict
        })

    # Route handler for a search and for question submission
    @app.route('/questions', methods=['POST'])
    def post_question():
        # if the request sent was a search request
        if('searchTerm' in json.loads(request.data)):
            search_term = json.loads(request.data)['searchTerm']
            questions = Question.query.filter(Question.question.ilike('%' +
                                              search_term + '%')).all()
        # if not, it was a request to add a new question
        else:
            question_data = json.loads(request.data)

            # If the question or answer sent are empty, returns an error.
            # Otherwise creates a new Question object.
            if(question_data['question'] == '' or
               question_data['answer'] == ''):
                abort(422)
            else:
                question = Question(question=question_data['question'],
                                    answer=question_data['answer'],
                                    difficulty=question_data['difficulty'],
                                    category=question_data['category'])

            # Try to add the new question to the database
            try:
                question.insert()
                questions = Question.query.all()
            except Exception as e:
                abort(422)

        # Gets paginated questions for display. If there was a search, the
        # questions are the ones matching the search filter. If the user added
        # a question, it simply returns all questions.
        current_page = request.args.get('page', 1, type=int)
        paginated_questions_list = paginate_questions(questions, current_page)

        return jsonify({
            'success': True,
            'questions': paginated_questions_list,
            'total_questions': len(questions)
        })

    # Route handler for category pages
    @app.route('/categories/<category_id>/questions')
    def load_category_questions(category_id):
        # Gets the questions belonging to the current category and paginates.
        questions = Question.query.filter(Question.category == category_id).\
                                          all()
        current_page = request.args.get('page', 1, type=int)
        paginated_questions_list = paginate_questions(questions, current_page)

        # if the page is out of bounds or the category doesn't exist
        if(len(paginated_questions_list) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'current_page': current_page,
            'questions': paginated_questions_list,
            'total_questions': len(questions),
            'current_category': category_id
        })

    # Route handler question deletion
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).\
                                         one_or_none()
        current_page = request.args.get('page', 1, type=int)

        # If the question doesn't exist, abort; otherwise delete
        if(question is None):
            abort(422)
        else:
            question.delete()
            total_questions = Question.query.all()
            paginated_questions_list = paginate_questions(total_questions,
                                                          current_page)
            total_questions_num = len(total_questions)

        return jsonify({
            'success': True,
            'question': int(question_id),
            'total_questions': total_questions_num,
            'questions': paginated_questions_list
        })

    # Route handler for the categories list (for the new question page / quiz)
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories_dict = {}

        # Creates a dictionary from all category objects.
        for category in categories:
            categories_dict[category.id] = category.type

        # if there are no categories, abort
        if(len(categories_dict) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories_dict
        })

    # Route handler for the quiz
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        # Sets the next question to '' in order to account for 'no questions
        # left' case. Gets the previous questions and category ID from request.
        next_question = ''
        category = json.loads(request.data)['quiz_category']
        category_id = int(category['id'])
        previous_questions = json.loads(request.data)['previous_questions']

        # if the category number is 0, the user chose 'all', so all questions
        # are valid
        if(category_id == 0):
            questions = Question.query.all()
        # if the user chose a category
        else:
            questions = Question.query.filter(Question.category ==
                                              category_id).all()

        # Checks whether the question was already asked, if it was,
        # continue to the next question in the database. If it wasn't,
        # set this as the next quesiton and break from the loop.
        for question in questions:
            if(question.id in previous_questions):
                continue
            else:
                next_question = question.format()
                break

        return jsonify({
            'success': True,
            'question': next_question,
            'category': category_id
        })

    # Error handler for "bad request" cases
    @app.errorhandler(400)
    def bad_request_handler(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request.'
        }), 400

# Error handler for "not found" cases
    @app.errorhandler(404)
    def not_found_handler(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found. The page you asked for does not exist.'
        }), 404

    # Error handler for "unprocessable" cases
    @app.errorhandler(422)
    def unprocessable_handler(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity. Used identifier is incorrect.'
        }), 422

    # Error handler for "internal server error" cases
    @app.errorhandler(500)
    def internal_server_error_handler(error):
        print(sys.exc_info())
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error.'
        }), 500

    return app
