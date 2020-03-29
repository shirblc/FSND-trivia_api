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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Test for loading the main page (question list)
    def get_questions(self):
        response = self.client().get('/questions')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(res_data['success'])
        self.assertEqual(len(res_data['questions']), 10)
        self.assertEqual(res_data['current_page'], 1)
        self.assertTrue(len(res_data['categories']))

    # Test for the pagination (checking page 2)
    def get_page_two_questions(self):
        response = self.client().get('/questions?page=2')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(res_data['questions']), 10)
        self.assertEqual(res_data['current_page'], 2)
        self.assertTrue(res_data['success'])

    # Test for an out-of-bounds questions page
    def get_out_of_bounds_page(self):
        response = self.client().get('/questions?page=100')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(res_data['success'])
        self.assertFalse(len(res_data['questions']))

    # Test for a category questions pages
    def get_category_page(self):
        response = self.clien().get('/categories/1/questions')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(res_data['category'], 1)
        self.assertTrue(len(res_data['questions']))
        self.assertTrue(res_data['success'])

    # Test for an out-of-bounds category questions pages
    def get_out_of_bounds_category(self):
        response = self.client().get('/categories/100/questions')
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(res_data['success'])
        self.assertFalse(len(res_data['questions']))

    # Test for the search with a term that exists in the database
    def post_search_term(self):
        response = self.client().post('/questions', json={'searchTerm':'title'})
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(res_data['questions'], 2)
        self.assertTrue(len(res_data['questions']))
        self.assertTrue(res_data['success'])

    # Test for search with term that doesn't exist in the database
    def post_search_nonexistent_term(self):
        response = self.client().post('/questions', json={'searchTerm':'meow'})
        res_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(res_data['success'])
        self.assertFalse(len(res_data['questions']))

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
