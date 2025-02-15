from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from trends import get_searches
from googleForm import generate_questions, create_google_form
from Mentor import generate_response
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("secretkey")

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

@app.route("/mentor", methods=["GET"])
def mentor():
    """Render the Mentor AI page with conversation history."""
    if "messages" not in session:
        session["messages"] = []
    return render_template("mentor.html", messages=session["messages"])

@app.route("/chat", methods=["POST"])
def chat():
    """Handle user messages and generate AI responses."""
    user_input = request.form.get("message")
    mode = request.form.get("mode", "idea_validation")  # Default mode

    if not user_input:
        return redirect(url_for("mentor"))

    response = generate_response(user_input, mode)

    # Store conversation history in session
    if "messages" not in session:
        session["messages"] = []
    
    session["messages"].append({"role": "user", "content": user_input})
    session["messages"].append({"role": "assistant", "content": response})
    session.modified = True  # Save session changes

    return redirect(url_for("mentor"))

@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    """Clear the conversation history."""
    session.pop("messages", None)  # Remove messages from session
    return redirect(url_for("mentor"))

if __name__ == "__main__":
    app.run(debug=True)


