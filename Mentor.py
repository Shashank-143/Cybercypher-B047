import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("s_mentor_apikey")
if not api_key:
    raise ValueError("s_mentor_apikey environment variable is not set.")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

repo_id = "microsoft/Phi-3.5-mini-instruct"
model_url = f"https://api-inference.huggingface.co/models/{repo_id}"
conversation_history = []

# Initialize tools
tools = {
    "idea_validation": {
        "name": "Idea Validation",
        "description": "Validate and analyze business ideas",
        "prompt": (
            "As a startup advisor specializing in idea validation, analyze this business idea in short but detail:\n"
            "1. Market potential and size\n"
            "2. Competition analysis\n"
            "3. Feasibility assessment\n"
            "4. Unique value proposition\n"
            "5. Initial target market\n"
            "6. Key risks and challenges\n"
            "7. Implementation roadmap\n\n"
            "Provide specific, actionable feedback and suggestions."
        )
    },
    "market_research": {
        "name": "Market Research",
        "description": "Detailed market analysis and insights",
        "prompt": (
            "As a market research expert, provide short but comprehensive analysis covering:\n"
            "1. Market size and growth potential\n"
            "2. Target customer segments and demographics\n"
            "3. Competitive landscape and market leaders\n"
            "4. Market trends and future projections\n"
            "5. Entry barriers and regulations\n"
            "6. Distribution channels\n"
            "7. Market gaps and opportunities"
        )
    },
    "business_plan": {
        "name": "Business Plan Development",
        "description": "Create short but detailed business plans",
        "prompt": (
            "As a business strategist, develop a comprehensive plan addressing:\n"
            "1. Business model and value chain\n"
            "2. Revenue streams and pricing strategy\n"
            "3. Cost structure and margins\n"
            "4. Growth strategy and scaling plan\n"
            "5. Financial projections and metrics\n"
            "6. Operational requirements\n"
            "7. Risk mitigation strategies"
        )
    },
    "pitch_deck": {
        "name": "Pitch Deck Creation",
        "description": "Guide for creating investor presentations",
        "prompt": (
            "As a pitch consultant, provide short but detailed guidance for creating compelling investor materials:\n"
            "1. Problem statement and solution\n"
            "2. Market opportunity and timing\n"
            "3. Business model and revenue strategy\n"
            "4. Traction and key metrics\n"
            "5. Competitive advantage\n"
            "6. Team and expertise\n"
            "7. Funding requirements and use of funds"
        )
    }
}

def format_prompt(user_input, mode):
    """Format the prompt with context and conversation history."""
    tool = tools[mode]
    context_lines = [
        f"System: {tool['prompt']}",
        "Provide a brief but actionable response. Keep it concise and focus on key insights.",
        ""
    ]

    if conversation_history:
        relevant_history = [
            msg for msg in conversation_history[-4:]
            if msg.get('mode') == mode
        ]
        if relevant_history:
            history = [
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in relevant_history
            ]
            context_lines.extend(["Previous relevant conversation:", *history, ""])

    context_lines.extend([f"User: {user_input}", "Assistant:"])
    return "\n".join(context_lines)

def generate_response(user_input, mode):
    """Generate an AI response using the specified mode."""
    if not user_input.strip():
        return "Error: Empty input provided."

    prompt = format_prompt(user_input, mode)

    try:
        response = requests.post(
            model_url,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 300,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "do_sample": True
                }
            },
            timeout=30
        )

        if response.status_code == 401:
            return "Error: API authentication failed. Please check your API key."
        if response.status_code != 200:
            return f"Error: API request failed with status code {response.status_code}"

        result = response.json()
        if isinstance(result, list) and result:
            response_text = result[0].get('generated_text', '').strip()
        else:
            response_text = result.get('generated_text', '').strip()

        if not response_text:
            return "Error: Empty response received from API."

        # Update conversation history
        timestamp = datetime.now().isoformat()
        conversation_history.extend([
            {"role": "user", "content": user_input, "mode": mode, "timestamp": timestamp},
            {"role": "assistant", "content": response_text, "mode": mode, "timestamp": timestamp}
        ])

        return response_text

    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error: API request failed - {str(e)}"
    except Exception as e:
        return f"Error generating response: {str(e)}"