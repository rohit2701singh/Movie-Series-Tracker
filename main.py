from flask import Flask, render_template, redirect, request, flash, url_for
from forms import SearchForm
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()


TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE_URL = "https://image.tmdb.org/t/p/w200"

headers = { 
    "Content-Type": "application/json;charset=utf-8",
    "Authorization": os.getenv('Authorization_Key')
}

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv('FLASK_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wishlist.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)


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


with app.app_context():
    db.create_all()


@app.route("/")
def home():

    # movies_watched = db.session.execute(
    #     db.select(Wishlist).where(Wishlist.media_type=="movie").where(Wishlist.status=="watched")
    # ).scalars().all()
    # print(len(movies_watched))

    # for counter at home screen
    movies_watched = db.session.execute(
        db.select(Wishlist).where(Wishlist.media_type=="movie", Wishlist.status=="watched")
    ).scalars().all()

    movies_towatch = db.session.execute(
        db.select(Wishlist).where(Wishlist.media_type=="movie", Wishlist.status=="towatch")
    ).scalars().all()

    series_watched = db.session.execute(
        db.select(Wishlist).where(Wishlist.media_type=="series", Wishlist.status=="watched")
    ).scalars().all()

    series_towatch = db.session.execute(
        db.select(Wishlist).where(Wishlist.media_type=="series", Wishlist.status=="towatch")
    ).scalars().all()


    # for recent activity
    recent_movies = db.session.execute(
        db.select(Wishlist)
        .where(Wishlist.media_type == "movie")
        .order_by(Wishlist.id.desc())
        .limit(4)
    ).scalars().all()

    recent_series = db.session.execute(
        db.select(Wishlist)
        .where(Wishlist.media_type == "series")
        .order_by(Wishlist.id.desc())
        .limit(4)
    ).scalars().all()

    
    return render_template(
        "home.html",
        movies_watched = len(movies_watched),
        movies_towatch = len(movies_towatch),
        series_watched = len(series_watched),
        series_towatch = len(series_towatch),
        recent_movies = recent_movies,
        recent_series = recent_series
    )



@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    results = []

    # current page (default 1)
    page = request.args.get("page", 1, type=int)

    # fallback values in case of GET without form submit
    query = request.args.get("q", "")
    status = request.args.get("status", "all")

    if form.validate_on_submit():
        query = form.q.data
        status = form.status.data

    if query:  # only search if query is provided
        # Search Movies
        if status in ["movie", "all"]:
            url_movie = f"{TMDB_BASE_URL}/search/movie"
            params_movie = {"query": query, "page": page}
            resp_movie = requests.get(url_movie, headers=headers, params=params_movie).json()
            for item in resp_movie.get("results", []):
                item["media_type"] = "movie"

                # 🔹 format date
                date_str = item.get("release_date")
                item["formatted_date"] = (
                    datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
                    if date_str else "N/A"
                )

                results.append(item)

        # Search TV/Series
        if status in ["series", "all"]:
            url_tv = f"{TMDB_BASE_URL}/search/tv"
            params_tv = {"query": query, "page": page}
            resp_tv = requests.get(url_tv, headers=headers, params=params_tv).json()
            for item in resp_tv.get("results", []):
                item["media_type"] = "series"

                # 🔹 format date
                date_str = item.get("first_air_date")
                item["formatted_date"] = (
                    datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
                    if date_str else "N/A"
                )

                results.append(item)


    # fixed 3 pages max
    total_pages = 5

    return render_template(
        "search.html",
        form=form,
        results=results,
        page=page,
        total_pages=total_pages,
        query=query,
        status=status,
    )



@app.route("/wishlist/add", methods=["POST"])
def add_to_wishlist():

    # Get data from form
    tmdb_id = request.form.get("tmdb_id")
    media_type = request.form.get("media_type")
    title = request.form.get("title")
    release_date = request.form.get("release_date")
    poster_path = request.form.get("poster_path")
    overview = request.form.get("overview")
    rating = request.form.get("rating")
    vote_count = request.form.get("vote_count")
    original_language = request.form.get("original_language")
    popularity = request.form.get("popularity")
    user_rating = request.form.get("user_rating")  # optional, can be empty
    notes = request.form.get("notes")  # optional, can be empty

    # Check if already in wishlist
    existing_item = db.session.execute(db.select(Wishlist).where((Wishlist.tmdb_id == tmdb_id) & (Wishlist.media_type == media_type))).scalar()

    if existing_item:
        flash(f'"{title}" {media_type} is already in your Watchlist!', "warning")
        return redirect(request.referrer)   # user goes back to the search results, not to a blank or unrelated page

    # Create new Wishlist item
    new_item = Wishlist(
        tmdb_id=tmdb_id,
        media_type=media_type,
        title=title,
        release_date=datetime.strptime(release_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
        poster_path=f"{TMDB_IMG_BASE_URL}{poster_path}",
        overview=overview,
        rating=rating,
        vote_count=vote_count,
        original_language=original_language,
        popularity=popularity,
        status="towatch",      # default status
        user_rating=user_rating or None,  # optional
        notes=notes or None              # optional
    )

    db.session.add(new_item)
    db.session.commit()
    flash(f'"{title}" {media_type} added to your Watchlist!', "success")

    return redirect(request.referrer)  # Go back to search page



@app.route("/dashboard/<media_type>")
def dashboard(media_type):
    page = request.args.get("page", 1, type=int)  # current page
    per_page = 3  # items per page

    if media_type not in ["movie", "series"]:
        return redirect(url_for("home"))

    q = request.args.get("q", "")
    status_filter = request.args.get("status", "")
    sort_by = request.args.get("sort", "")

    # Start building query
    query = db.select(Wishlist).where(Wishlist.media_type == media_type)

    if q:
        query = query.where(Wishlist.title.ilike(f"%{q}%"))

    if status_filter in ["watched", "towatch"]:
        query = query.where(Wishlist.status == status_filter)

    if sort_by == "rating":
        query = query.order_by(Wishlist.rating.desc())
    elif sort_by == "date_added":
        query = query.order_by(Wishlist.date_added.desc())
    elif sort_by == "title":
        query = query.order_by(Wishlist.title.asc())

    # Use paginate
    items = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return render_template(
        "dashboard.html",
        items=items,
        media_type=media_type,
        q=q,
        status_filter=status_filter,
        sort_by=sort_by
    )


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    # Fetch the item from DB
    item = db.session.execute(db.select(Wishlist).where(Wishlist.id == item_id)).scalar()

    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("dashboard", media_type="movie"))  # fallback

    if request.method == "POST":
        # Get form data from modal
        status = request.form.get("status")
        user_rating = request.form.get("user_rating")
        notes = request.form.get("notes")

        # Update fields
        item.status = status
        item.user_rating = float(user_rating) if user_rating else None
        item.notes = notes or None

        # Commit changes
        db.session.commit()
        flash(f"{item.title} has been updated successfully!", "success")

        # Redirect back to edit page or dashboard
        return redirect(url_for("edit_item", item_id=item.id))

    # GET request: show edit page
    return render_template("edit.html", item=item)


@app.route("/wishlist/delete/<int:item_id>")
def delete_item(item_id):
    item = db.session.execute(db.select(Wishlist).where(Wishlist.id == item_id)).scalar()
    db.session.delete(item)
    db.session.commit()
    flash(f'"{item.title}" has been deleted.', 'success')
    return redirect(request.referrer or url_for('dashboard', media_type=item.media_type))


if __name__ == '__main__':
    app.run(debug=True)