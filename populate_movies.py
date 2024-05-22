import requests
from app import app
from datetime import datetime
from models.movie import Movie, Genre, db

TMDB_API_KEY = '928a86fa32cd492578b2921001b702a1'
TMDB_ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5MjhhODZmYTMyY2Q0OTI1NzhiMjkyMTAwMWI3MDJhMSIsInN1YiI6IjY2MTljZGY3OGMzMTU5MDE5M2MwZTBjYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJ'

def fetch_movies_from_tmdb():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&access_token={TMDB_ACCESS_TOKEN}"
    response = requests.get(url)
    data = response.json()
    movies = data.get('results', [])
    return movies

def fetch_genres_from_tmdb():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&access_token={TMDB_ACCESS_TOKEN}"
    response = requests.get(url)
    data = response.json()
    genres = data.get('genres', [])
    return genres

def populate_database():
    movies = fetch_movies_from_tmdb()
    genres = fetch_genres_from_tmdb()

    # Create a dictionary to map genre IDs to Genre objects
    genre_dict = {genre.id: genre for genre in Genre.query.all()}

    for movie_data in movies:
        title = movie_data['title']
        release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date() if movie_data['release_date'] else None
        new_movie = Movie(title=title, release_date=release_date)

        # Assign genres to the movie
        for genre_id in movie_data['genre_ids']:
            if genre_id in genre_dict:
                new_movie.genres.append(genre_dict[genre_id])
            else:
                # Create a new Genre object if it doesn't exist
                genre_name = next((genre['name'] for genre in genres if genre['id'] == genre_id), None)
                if genre_name:
                    new_genre = Genre(name=genre_name)
                    db.session.add(new_genre)
                    genre_dict[genre_id] = new_genre
                    new_movie.genres.append(new_genre)

        db.session.add(new_movie)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        populate_database()