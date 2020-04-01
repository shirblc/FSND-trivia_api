import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('localhost:5432',
                                                       self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # Index Route Tests ('/', GET)
    # -------------------------------------------------------

    # Test to ensure the home route redirects to the questions list
    def test_get_home_page(self):
        response = self.client().get('/')

        self.assertEqual(response.status_code, 302)

    # Questions Page Tests ('/questions', GET)
    # -------------------------------------------------------

    # Test for loading the main page (question list)
    def test_get_questions(self):
        response = self.client().get('/questions')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(res_data['success'])
        self.assertEqual(len(res_data['questions']), 10)
        self.assertEqual(res_data['current_page'], 1)
        self.assertTrue(len(res_data['categories']))

    # Test for the pagination (checking page 2)
    def test_get_page_two_questions(self):
        response = self.client().get('/questions?page=2')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(res_data['questions']), 8)
        self.assertEqual(res_data['current_page'], 2)
        self.assertTrue(res_data['success'])

    # Test for an out-of-bounds questions page
    def test_get_out_of_bounds_page(self):
        response = self.client().get('/questions?page=100')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(res_data['success'])

    # Search and New Questions route tests ('/questions', POST)
    # -------------------------------------------------------

    # Test for the search with a term that exists in the database
    def test_post_search_term(self):
        response = self.client().post('/questions', json={'searchTerm':
                                                          'title'})
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(res_data['questions']), 2)
        self.assertTrue(res_data['success'])

    # Test for search with term that doesn't exist in the database
    def test_post_search_nonexistent_term(self):
        response = self.client().post('/questions', json={'searchTerm':
                                                          'meow'})
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(res_data['success'])
        self.assertFalse(len(res_data['questions']))

    # Test for adding a new question
    def test_post_new_question(self):
        new_question = '{\
        "question": "What is the longest running science fiction show?",\
        "answer": "Doctor Who",\
        "difficulty": 2,\
        "category": 5 }'
        response = self.client().post('/questions', data=new_question)

        res_data = json.loads(response.data)
        added_question = Question.query.get(24)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_question[22:71], added_question.question)
        self.assertTrue(res_data['success'])

    # Test for adding an empty question
    def test_error_post_empty_question(self):
        new_question = '{\
        "question": "",\
        "answer": "",\
        "difficulty": 0,\
        "category": 0 }'
        response = self.client().post('/questions', data=new_question)
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(res_data['success'])

    # Questions-By-Category Pages Tests ('/categories/<id>/questions', GET)
    # -------------------------------------------------------

    # Test for a category questions pages
    def test_get_category_page(self):
        response = self.client().get('/categories/1/questions')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(res_data['current_category'], '1')
        self.assertTrue(len(res_data['questions']))
        self.assertTrue(res_data['success'])

    # Test for an out-of-bounds category page
    def test_get_out_of_bounds_category_page(self):
        response = self.client().get('/categories/1/questions?page=50')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(res_data['success'])

    # Test for an out-of-bounds category
    def test_get_out_of_bounds_category(self):
        response = self.client().get('/categories/100/questions')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(res_data['success'])

    # Question Deletion Route Tests ('/questions/<id>', DELETE)
    # -------------------------------------------------------

    # Test for deleting an existing question
    def test_delete_existing_question(self):
        response = self.client().delete('/questions/2')
        res_data = json.loads(response.data)
        deleted_question = Question.query.filter(Question.id ==
                                                 2).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(deleted_question)
        self.assertEqual(res_data['question'], 2)
        self.assertEqual(res_data['total_questions'], 18)
        self.assertTrue(res_data['success'])

    # Test for deleting a question that doesn't exist
    def test_delete_nonexistent_question(self):
        response = self.client().delete('/questions/100')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(res_data['success'])

    # Categories List Route Tests ('/categories', GET)
    # -------------------------------------------------------

    # Test for getting categories
    def test_get_categories(self):
        response = self.client().get('/categories')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(res_data['categories']), 6)
        self.assertTrue(res_data['success'])

    # Quiz Route Tests ('/quizzes', POST)
    # -------------------------------------------------------

    # Test for quiz by category
    def test_quiz_with_category(self):
        quiz_data = '{\
        "previous_questions": [],\
        "quiz_category": {"type": "Science", "id": "1"} }'
        response = self.client().post('/quizzes', data=quiz_data)
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(res_data['category'], 1)
        self.assertTrue(res_data['success'])

    # Test for quiz without category (all option)
    def test_quiz_all_categories(self):
        quiz_data = '{\
        "previous_questions": [],\
        "quiz_category": {"type": "None", "id": "0"} }'
        response = self.client().post('/quizzes', data=quiz_data)
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(res_data['category'], 0)
        self.assertTrue(res_data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
