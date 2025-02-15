from flask import Flask, request, jsonify
import os
import ast
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import requests

load_dotenv()
apikey = os.getenv("d_filter_apikey")
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
client = InferenceClient(api_key=apikey)

def get_searches(query):
    
    API_KEY = os.getenv("d_search_apikey")
    query = query

    params_related = {"q": query, "api_key": API_KEY, "engine": "google","nums":200}
    related_res = requests.get("https://serpapi.com/search", params=params_related)

    params_auto = {"q": query, "api_key": API_KEY, "engine": "google_autocomplete"}
    auto_res = requests.get("https://serpapi.com/search", params=params_auto)

    related_searches = related_res.json().get("related_searches", []) if related_res.status_code == 200 else []
    autocomplete_suggestions = auto_res.json().get("suggestions", []) if auto_res.status_code == 200 else []

    context=[]
    for i, item in enumerate(related_searches, 1):
        if ((list(item.keys()))[1])=='query':
            context.append(item['query'])

    for i, item in enumerate(autocomplete_suggestions, len(related_searches) + 1):
        context.append(item['value'])
    return check_searches(context, query)


def check_searches(context, query):
    query_template = f"""
    Given the context: {context}, filter it based on the query: {query}. 
    If the context is unrelated to {query}, do not return anything. 
    Otherwise, return the relevant results as a list separated by commas. 
    Do not include movies or songs or books. Make sure the output is a unique list.
    Do not write context word before or after just provide answers.
    """

    messages = [
        {"role": "system", "content": query_template},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
    ] 

    response = client.chat.completions.create(
        model=repo_id,
        messages=messages
    )

    my_response = response['choices'][0]['message']['content']
    return my_response.split(',')

def string_to_list(string_input):
    try:
        return ast.literal_eval(string_input)
    except (ValueError, SyntaxError):
        print("Invalid input format")
        return []

