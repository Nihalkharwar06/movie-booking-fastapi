"""python version 3.10.1."""
import os # Standard Library Imports
from typing import List
from datetime import datetime
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer  # Grouped import statement
from firebase_admin import auth, initialize_app
from pydantic import BaseModel
from google.cloud import firestore

app = FastAPI()

# Initialize Firebase app
initialize_app()

# Firebase connection
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] =  "./booming-tooling-384907-14d84f09490c.json"

# OAuth2PasswordBearer for handling authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# User Information
class UserInfo(BaseModel):
    """User Info parameter"""
    name : str
    age : int
    seats : int


#User model
class User(BaseModel):
    """User parameters"""
    email: str
    password: str


#Movie model
class Movie(BaseModel):
    """Movie parameters"""
    id: str
    title: str
    description: str
    genre: str
    available_seats: int
    price: float
    release_date: datetime
    location: str


# User registration API
@app.post("/register")
def register_user(user: User):
    """Create a new user in Firebase Authentication."""
    try:
        user = auth.create_user(
            email=user.email,
            password=user.password,
        )
        return {"message": "User registered successfully"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


# User login API
@app.post("/login")
def login_user(user: User):
    """Sign in with email and password in Firebase Authentication."""
    try:
        user = auth.get_user_by_email(user.email)
        return {"message": "User logged in successfully", "uid": user.uid}
    except auth.AuthError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error


# Initialize Firestore client
db = firestore.Client()


# API endpoint to add a movie
@app.post("/movies")
def add_movie(movie: Movie):
    """Add movie to Firestore collection."""
    movie_dict = movie.dict()
    print("Movie",movie_dict)
    # Add movie to Firestore collection
    db.collection('movies').document(movie.id).set(movie_dict)
    return {"message": "Movie added successfully"}


# API endpoint to get list of all movies
@app.get("/movies", response_model=List[Movie])
def get_movies():
    """Get all movies from Firestore collection."""
    movies = db.collection('movies').get()
    movies_list = [Movie(**movie.to_dict()) for movie in movies]
    return movies_list


# API endpoint to get list of all movies
@app.get("/", response_model=List[Movie])
def get_all_movies():
    """Get all movies from Firestore collection."""
    movies = db.collection('movies').get()
    movies_list = [Movie(**movie.to_dict()) for movie in movies]
    return movies_list


# API endpoint to book a movie
@app.post("/movies/{movie_id}/{name}/{mobile_number}/{number_of_seats}/book")
def book_movie(*,number_of_seats: int,movie_id: str,name : str , mobile_number: int):
    """Check if movie exists in Firestore and number of seats"""
    movie_ref = db.collection('movies').document(movie_id)
    movie = movie_ref.get()
    if movie.exists:
        # Get movie data
        movie_data = movie.to_dict()
        # Set user information
        user_info = {
            'name':name,
            'number':mobile_number,
            'seats':number_of_seats,
            'total_price':movie_data['price']*number_of_seats
        }
        available_seats = movie_data.get('available_seats', 0)
        if available_seats > 0:
            # Decrease available seats by 1
            movie_data['available_seats'] = available_seats - number_of_seats
            # Update movie data in Firestore
            movie_ref.update(movie_data)
            # Add user info to UserInfo collection
            db.collection('UserInfo').document(movie_id).set(user_info)

            return {"message": "Movie booked successfully"}
        return {"error": "No available seats for the movie"}
    return {"error": "Movie not found"}
