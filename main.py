from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html") 


@app.route("/movie-dashboard")
def movie_dashboard():
    return render_template("movie_dashboard.html") 


@app.route("/series-dashboard")
def series_dashboard():
    return render_template("series_dashboard.html") 


@app.route("/search")
def search():
    return render_template("search.html") 


if __name__ == '__main__':
    app.run(debug=True)