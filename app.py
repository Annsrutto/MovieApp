#!/usr/bin/python3
"""This contains configuration for connecting to MySQL Database."""

from models.movie import Movie, db
from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/movies', methods=['GET'])
def get_all_movies():
    movies = Movie.query.all()
    movie_list = [movie.serialize() for movie in movies]
    return jsonify(movie_list)

@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.route('/movies', methods=['POST'])
def add_movies():
    try:
        data = request.json
        title = data.get('title')
        release_date = data.get('release_date', None)
        genre_ids = data.get('genre_ids', [])

        if not title:
            return jsonify({'error': 'Title required'}), 400

        new_movie = Movie(title=title, release_date=release_date)

        if genre_ids:
            genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            new_movie.genres.extend(genres)

        new_movie.save()

        response_data = {
            'message': 'Movie added successfully',
            'movie': new_movie.serialize()
        }
        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['GET'])
def search_movies():
    title = request.args.get('title')
    release_date = request.args.get('release_date')
    genre_name = request.args.get('genre_name')

    query = Movie.query

    if title:
        query = query.filter(Movie.title.ilike(f'%{title}%'))
    if genre_name:
        query = query.join(Movie.genres).filter(Genre.name.ilike(f'%{genre_name}%'))
    if release_date:
        query = query.filter(Movie.release_date == release_date)

    movies = query.all()

    if movies:
        movie_list = [movie.serialize() for movie in movies]
        return jsonify({'movies': movie_list}), 200
    else:
        return jsonify({'message': 'No movies found matching search criteria'}), 200

@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        movie = Movie.query.get(movie_id)
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404

        title = data.get('title')
        release_date = data.get('release_date')
        genre_ids = data.get('genre_ids', [])

        if title:
            movie.title = title
        if release_date:
            movie.release_date = release_date
        if genre_ids:
            genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            movie.genres = genres

        db.session.commit()

        return jsonify({'message': 'Movie updated successfully', 'movie': movie.serialize()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/movies/<int:id>', methods=['DELETE'])
def delete_movie(id):
    movie = Movie.query.get(id)
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404

    try:
        db.session.delete(movie)
        db.session.commit()
        return jsonify({'message': 'Movie deleted successfully'}), 204
    except Exception as e:
        return jsonify({'message': 'Failed to delete movie', 'error': str(e)}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
