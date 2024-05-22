#!/usr/bin/python3
"""This module contains the class models for the movie collection API."""
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy.orm import validates
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table

db = SQLAlchemy()

# Association table for many-to-many relationship between Movie and Genre
movie_genre_table = Table(
    'movie_genre',
    db.Model.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.Date)
    genres = db.relationship('Genre', secondary=movie_genre_table, backref='movies')

    def __init__(self, title, release_date=None):
        self.title = title
        self.release_date = release_date

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': str(self.release_date),
            'genres': [genre.name for genre in self.genres]
        }

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title is required")
        return title

    @validates('release_date')
    def validate_release_date(self, key, release_date):
        if isinstance(release_date, str):
            try:
                datetime.strptime(release_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Invalid date format, should be YYYY-MM-DD")
        elif release_date is not None:
            if not isinstance(release_date, date):
                raise ValueError("release_date must be a date object or a string in the format YYYY-MM-DD")
        return release_date

    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"

class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"
