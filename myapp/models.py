from datetime import timezone, datetime
from flask_login import UserMixin
from myapp import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).where(User.id == user_id)).scalar()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self): # When you print an object of class, __repr__ defines what gets displayed.
        return f"<User Detail: User({self.username}, {self.email})>"


class Wishlist(db.Model):
    __tablename__ = "wishlist"

    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, nullable=False)
    media_type = db.Column(db.String(10), nullable=False)  # movie or series
    title = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.String(20))  # store as string "dd-mm-yyyy" or original from TMDB
    poster_path = db.Column(db.String(255))
    overview = db.Column(db.Text)
    rating = db.Column(db.Float)  # vote_average
    vote_count = db.Column(db.Integer)
    original_language = db.Column(db.String(10))
    popularity = db.Column(db.Float)
    status = db.Column(db.String(20), nullable=False, default="towatch")  # "watched" or "towatch"
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_rating = db.Column(db.Float, nullable=True)  # optional
    notes = db.Column(db.Text, nullable=True)  # optional

    def __repr__(self):
        return f"<Wishlist {self.title} ({self.media_type})>"
