from flask import Flask, jsonify, request, render_template, redirect, url_for
from trends import get_searches
from googleForm import generate_questions, create_google_form

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/trends", methods = ["GET", "POST"])
def trends():
    top_searches = None
    if request.method == "POST":
        key_word = request.form.get("query")
        if key_word:
            print(type(key_word))
            top_searches = get_searches(key_word)  # Fetch search results
            print("DEBUG - Search results:", top_searches)
    return render_template("trends.html", results=top_searches)

@app.route("/form", methods=["GET", "POST"])
def form():
    link = None
    if request.method == "POST":
        idea = request.form.get("idea")
        questions = generate_questions(idea)
        link = create_google_form(idea=idea, questions=questions)
        print(questions, link)
            
    return render_template("googleForm.html", form_link=link)

@app.route("/mentor", methods = ["GET", "POST"])
def mentor():
    return render_template("mentor.html")

if __name__ == "__main__":
    app.run(debug=True)


