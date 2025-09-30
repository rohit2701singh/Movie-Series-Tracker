from flask import Flask, render_template, redirect, request
from forms import SearchForm
import requests
from datetime import datetime
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


@app.route("/")
def home():
    return render_template("home.html") 


@app.route("/movie-dashboard")
def movie_dashboard():
    return render_template("movie_dashboard.html") 


@app.route("/series-dashboard")
def series_dashboard():
    return render_template("series_dashboard.html") 



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




if __name__ == '__main__':
    app.run(debug=True)