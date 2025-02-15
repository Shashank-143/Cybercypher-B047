from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from huggingface_hub import InferenceClient
import json
import os

def generate_questions(idea):
    
    prompt = f"""
    Generate exactly 3 market research questions for the startup idea: "{idea}".
    
    The questions should cover:
    1. Market Need (Does this problem exist?)
    2. Target Audience (Who needs this?)
    3. Pricing Sensitivity (How much would users pay?)

    Return only a plain-text numbered list of questions.
    Example:
    1. How often do you face this problem?

    keep them very short and sweet and I want exactly three questions
    do not make more than three questions
    """

    response = client.text_generation(prompt, max_new_tokens=300)

    # Extract questions from AI response
    raw_questions = response.strip().split("\n")

    # Clean and filter questions
    structured_questions = []
    for line in raw_questions:
        line = line.strip()
        if line and line[0].isdigit():  # Ensure it's a valid question
            question_text = line.split(". ", 1)[-1]  # Remove number
            if "how much" in question_text.lower() or "price" in question_text.lower():
                structured_questions.append({
                    "question": question_text,
                    "type": "multiple_choice",
                    "options": ["₹0", "₹100-₹300", "₹300-₹500", "₹500+"]
                })
            elif "do you need" in question_text.lower() or "problem" in question_text.lower():
                structured_questions.append({"question": question_text, "type": "yes_no"})
            else:
                structured_questions.append({"question": question_text, "type": "text"})

    # Handle AI failure case
    if not structured_questions:
        structured_questions = [{"question": "Error: AI did not generate valid questions.", "type": "text"}]

    # Add mandatory demographic questions manually
    final_questions = [
        {"question": "What is your name?", "type": "text"},
        {"question": "How old are you?", "type": "number"},
        {"question": "What is your gender?", "type": "radio", "options": ["Male", "Female"]}
    ] + structured_questions

    return final_questions

def create_google_form(idea, questions):  

    # Step 1: Create a new Google Form
    form_metadata = {
        "info": {"title": f"Survey for: {idea}"}
    }
    form = service.forms().create(body=form_metadata).execute()
    form_id = form["formId"]

    # Step 2: Prepare properly formatted questions
    requests = []
    for index, q in enumerate(questions):  
        item = {
            "createItem": {
                "location": {"index": index},  
                "item": {
                    "title": q["question"],
                    "questionItem": {
                        "question": {"required": False}
                    }
                }
            }
        }

        # Handle different question types
        if q["type"] == "text":
            item["createItem"]["item"]["questionItem"]["question"]["textQuestion"] = {}
        elif q["type"] == "number":
            item["createItem"]["item"]["questionItem"]["question"]["textQuestion"] = {
                "paragraph": False  # Number inputs are still text fields in Google Forms
            }
        elif q["type"] == "multiple_choice" or q["type"] == "radio":
            item["createItem"]["item"]["questionItem"]["question"]["choiceQuestion"] = {
                "type": "RADIO",
                "options": [{"value": opt} for opt in q.get("options", [])]
            }
        elif q["type"] == "yes_no":
            item["createItem"]["item"]["questionItem"]["question"]["choiceQuestion"] = {
                "type": "RADIO",
                "options": [{"value": "Yes"}, {"value": "No"}]
            }

        requests.append(item)

    # Step 3: Send batch update request to add questions
    update_request = {"requests": requests}
    service.forms().batchUpdate(formId=form_id, body=update_request).execute()

    # Step 4: Return the form's edit link
    form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
    return form_url

