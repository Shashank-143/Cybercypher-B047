from flask import Flask, jsonify, request, render_template, redirect, url_for
import trends

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/trends", methods = ["GET", "POST"])
def trends():

    return render_template("trends.html")

@app.route("/form", methods = ["GET", "POST"])
def form():
    return render_template("googleForm.html")

@app.route("/mentor", methods = ["GET", "POST"])
def mentor():
    return render_template("mentor.html")

if __name__ == "__main__":
    app.run(debug=True)


