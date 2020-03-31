# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application.


## API Documentation

### Application Endpoints

1. GET '/'
2. GET '/questions'
3. POST '/questions'
4. GET '/categories/<category_id>/questions'
5. DELETE '/questions/<question_id>'
6. GET '/categories'
7. POST '/quizzes'

#### GET '/'
**Description**: Home route. Redirects to the questions route.
**Handler Function**: index.
**Request Arguments**: None.
**Required Data**: None.
**Returns**: Redirect.
**Expected Errors**: None.
**CURL**: `curl http://127.0.0.1:5000/`

#### GET '/questions'
**Description**: Questions endpoint to get all questions in the database, regardless of their category.
**Handler Function**: load_questions.
**Request Arguments**:
1. Page [Optional; defaults to 1] - Integer - States the page the user is currently viewing, thus determining which questions to display.
**Required Data**: None.
**Returns**: An object containing:
  - A success value ('success') - Boolean
  - The user's current page ('current_page') - Integer
  - The questions for the page ('questions') - List
  - The total number of questions in the database ('total_questions') - Integer
  - A dictionary containing all available categories ('categories') - Dictionary
**Expected Errors**:
  - 404 - In case there are no questions in the page the user asked for, the server returns a "not found" error.
**CURL**: `curl http://127.0.0.1:5000/questions`

#### POST '/questions'
**Description**: POST endpoint for searching the questions or for creating a new question.
**Handler Function**: post_question.
**Request Arguments**: None.
**Required Data**:
1. For search: A JSON containing the search term ('searchTerm', string).
2. For question submission: A JSON containing the required fields:
  - The question - 'question' - String.
  - The correct answer - 'answer' - String.
  - Difficulty level - 'difficulty' - Integer.
  - The category the question belongs to - 'category' - Integer.
**Returns**: An object containing:
  - A success value ('success') - Boolean
  - 'questions' - List
    1. For search - A list of questions matching the search criteria.
    2. For question submission - The first 10 questions in the database (redirects the user to the home page).
  - The total number of questions in the database ('total_questions') - Integer
2. For question submission:
**Expected Errors**:
  - 422 - For question submission. In case there's an error adding the new question to the database or the question the user submitted is empty, the server returns an "unprocessable" error.
**CURL**:
1. For search: `curl -X POST http://127.0.0.1:5000/questions -H "Content-Type: application/json" -d '{"searchTerm": "title"}'`
2. For question submission: `curl -X POST http://127.0.0.1:5000/questions -H "Content-Type: application/json" -d '{"question": "What is the longest running science fiction show?", "answer": "Doctor Who", "difficulty": 2, "category": 5}'`

#### GET '/categories/<category_id>/questions'
**Description**: GET endpoint for getting the list of questions belonging to the selected category.
**Handler Function**: load_category_questions.
**Request Arguments**:
1. category_id [Required] - Integer - the ID of the category to view.
2. Page [Optional; defaults to 1] - Integer - States the page the user is currently viewing, thus determining which questions to display.
**Required Data**: None.
**Returns**: An object containing:
  - A success value ('success') - Boolean
  - The user's current page ('current_page') - Integer
  - The questions for the page and category ('questions') - List
  - The total number of questions for the current category ('total_questions') - Integer
  - The ID of the current category ('current_category') - Integer
**Expected Errors**:
  - 404 - In case there are no questions in the page the user asked for, or there's no category with the ID the user asked for, the server returns a "not found" error.
**CURL**: `curl http://127.0.0.1:5000/categories/1/questions`

#### DELETE '/questions/<question_id>'
**Description**: DELETE endpoint to delete a question from the database.
**Handler Function**: delete_question.
**Request Arguments**:
1. question_id [required] - Integer - the ID of the question to delete.
**Required Data**: None.
**Returns**: An object containing:
  - A success value ('success') - Boolean
  - The deleted question's ID ('question') - Integer
  - The total number of questions in the database ('total_questions') - Integer
**Expected Errors**:
  - 422 - If the user attempts to delete a question that doesn't exist, the server returns an "unprocessable" error.
**CURL**: `curl -X DELETE http://127.0.0.1:5000/questions/2`

#### GET '/categories'
**Description**: GET endpoint to get the names of IDs of all the categories in the database.
**Handler Function**: get_categories.
**Request Arguments**: None.
**Required Data**: None.
**Returns**: An object containing:
  - A success value ('success') - Boolean
  - A dictionary with all the categories in the database ('categories') - Dictionary
**Expected Errors**:
  - 404 - If there are no categories in the database, the server returns a "not found" error.
**CURL**: `curl http://127.0.0.1:5000/categories`

#### POST '/quizzes'
**Description**: POST endpoint for playing the quiz. Gets the questions from the database and passes one question at a time to the frontend.
**Handler Function**: play_quiz.
**Request Arguments**: None.
**Required Data**: A JSON containing:
  - The category chosen for the quiz - quiz_category - Dictionary:
    - The name of the category - 'type' - String.
    - The ID of the category - 'id' - String.
  - The previously asked questions - previous_questions - List of Integers.
**Returns**: An object containing:
  - A success value ('success') - Boolean
  - The next question in the quiz ('question') - Dictionary.
  - The category chosen for the quiz ('category') - Integer.
**Expected Errors**: None.
**CURL**: `curl -X POST http://127.0.0.1:5000/questions -H "Content-Type: application/json" -d '{"previous_questions": [], "quiz_category": {"type": "None", "id": "0"}}'`


### Error Handlers

The app contains the following error handlers:
1. 400 - Bad Request
2. 404 - Not Found
3. 422 - Unprocessable Entity
4. 500 - Internal Server Error

For all errors, the server returns the following object:
  - A success value ('success') - Boolean
  - The HTTP status code ('error') - Integer
  - An explanation message ('message') - String


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
