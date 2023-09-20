import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

def paginate_books(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]
    return current_books

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to the Bookshelf API'
        })

    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars
    @app.route('/books', methods=['GET', 'POST'])
    def handle_books():
        if request.method == 'GET':
            return get_books()
        elif request.method == 'POST':
            return create_book()
    def get_books():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF
        books = Book.query.order_by(Book.id).all()
        current_books = paginate_books(request=request, selection=books)
        return jsonify({
            'success': True,
            'books': current_books,
            'total_books': len(books)
        })

    def create_book():
        book = Book(**request.get_json())
        selection = Book.query.order_by(Book.id).all()
        current_books = paginate_books(request=request, selection=selection)
        try:
            book.insert()
            return jsonify({
                'success': True,
                'created': book.id,
                'books': current_books,
                'total_books': len(selection),
            })
        except:
            return jsonify({
                'success': False,
                'error': 'An error occured while creating the book'
            }), 422


    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
    @app.route("/books/<int:book_id>", methods=['PATCH'])
    def update_book(book_id):
        book = Book.query.get(book_id)
        if not book:
            return jsonify({
                'success': False,
                'error': 'Book not found'
            }), 404
        data = request.get_json()

        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        if 'rating' in data:
            book.rating = data['rating']

        try:
            book.update()
            return jsonify({
                'success': True,
                'book_id': book.id,
            })
        except:
            return jsonify({
                'success': False,
                'error': 'An error occured while updating the book'
            }), 400

    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'

    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
    @app.route("/books/<int:book_id>", methods=['DELETE'])
    def delete_book(book_id):
        book = Book.query.get(book_id)
        if not book:
            return jsonify({
                'success': False,
                'error': 'Book not found'
            }), 404
        try:
            book.delete()
            return jsonify({
                'success': True,
                'deleted': book_id
            })
        except:
            return jsonify({
                'success': False,
                'error': 'An error occured while deleting the book'
            }), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found",
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable",
            }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "badrequest",
            }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed",
            }), 405
    return app