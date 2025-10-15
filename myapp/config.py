import os
from dotenv import load_dotenv

load_dotenv()

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE_URL = "https://image.tmdb.org/t/p/w200"

headers = { 
    "Content-Type": "application/json;charset=utf-8",
    "Authorization": os.getenv('Authorization_Key')
}


class Config:
    SECRET_KEY = os.getenv('FLASK_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///wishlist.db")