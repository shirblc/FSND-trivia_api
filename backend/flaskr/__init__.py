import os, json
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

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Origin', '*')
      response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
      return response

  # Function to paginate the questions and return them as a list
  def paginate_questions(questions, current_page):
      first_question_num = QUESTIONS_PER_PAGE * (current_page - 1)
      paginated_questions = questions[first_question_num:(first_question_num+9)]
      paginated_questions_list = []

      for question in paginated_questions:
          paginated_questions_list.append({
          'id': question.id,
          'question': question.question,
          'answer': question.answer,
          'category': question.category,
          'difficulty': question.difficulty
          })

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
      questions = Question.query.order_by(Question.id).all()
      current_page = request.args.get('page', 1, type=int)
      paginated_questions_list = paginate_questions(questions, current_page)
      categories = Category.query.all()
      categories_dict = {}

      for category in categories:
          categories_dict[category.id] = category.type

      if(len(paginated_questions_list) == 0):
          abort(404)

      return jsonify({
      'success': True,
      'current_page': current_page,
      'questions': paginated_questions_list,
      'total_questions': len(questions),
      'categories': categories_dict
      })

  # Route handler for a search
  @app.route('/questions', methods=['POST'])
  def post_question():

      # if the request sent was a search request
      if('searchTerm' in json.loads(request.data)):
          search_term = json.loads(request.data)['searchTerm']
          questions = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
      # if not, it was a request to add a new question
      else:
          question_data = json.loads(request.data)
          question = Question(question=question_data['question'], answer=question_data['answer'],
          difficulty=question_data['difficulty'], category=question_data['category'])

          # Try to add the new question to the database
          try:
              question.insert()
              questions = Question.query.all()
          except:
              abort(422)

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
      questions = Question.query.filter(Question.category == category_id).all()
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
      question = Question.query.filter(Question.id == question_id).one_or_none()

      # If the question doesn't exist, abort; otherwise delete
      if(question == None):
          abort(422)
      else:
          question.delete()
          total_questions = Question.query.all()

      return jsonify({
      'success': True,
      'question': question_id,
      'total_questions': total_questions
      })

  # Route handler for the categories list (for the new question page)
  @app.route('/categories')
  def get_categories():
      categories = Category.query.all()
      categories_dict = {}

      for category in categories:
          categories_dict[category.id] = category.type

      # if there are no categories, abort
      if(len(categories_dict) == 0):
          abort(404)

      return jsonify({
      'categories': categories_dict
      })

  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

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
      'message': 'Unprocessable Entity. The identifier you used is incorrect.'
    }), 422

  return app
