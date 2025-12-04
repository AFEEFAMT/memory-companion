import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from datetime import datetime
import re
import logging

load_dotenv()

# Configure the SDK with your API key from .env
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# System instructions for the persona "Kaya"
SYSTEM_INSTRUCTION = """
You are Kaya, a compassionate memory assistant for a patient with dementia.
Your goal is to identify the user's INTENT and generate a gentle, clear response.

CURRENT CONTEXT:
Time: {current_time}
Pending Tasks: {pending_tasks}

Output strict JSON with these keys:
1. "intent": One of ["manage_task", "save_memory", "recall_memory", "chat", "danger"]
2. "response_text": A warm, short sentence to speak to the user.
3. "parameters": (Optional) Data needed for the intent (e.g., task_name, due_datetime).

Example JSON:
{{"intent": "chat", "response_text": "I am doing well, how are you?", "parameters": {{}}}}
"""

def get_ai_response(user_text, pending_tasks_list):
    try:
        current_time = datetime.now().strftime("%A, %I:%M %p")
        tasks_str = ", ".join([t['task_name'] for t in pending_tasks_list]) or "None"
        
        # Inject context into the system prompt
        formatted_system_prompt = SYSTEM_INSTRUCTION.format(
            current_time=current_time, 
            pending_tasks=tasks_str
        )

        # Initialize the model with the specific system instruction
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=formatted_system_prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        # Send the user's message
        response = model.generate_content(user_text)
        clean_text = re.sub(r"```(json)?", "", response.text, flags=re.IGNORECASE).strip()
        return json.loads(clean_text)

    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        # Fallback safe response
        return {
            "intent": "chat", 
            "response_text": "I'm having a little trouble connecting, but I'm here with you."
        }

def synthesize_memory_answer(user_query, context_str):
    """
    Uses the LLM to answer a question based ONLY on the provided memory context.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = f"""
        You are Kaya. Answer the user's question gently, using ONLY the context below.
        If the context doesn't have the answer, say "I don't see a note about that."

        USER QUESTION: "{user_query}"
        
        MEMORY CONTEXT:
        {context_str}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logging.error(f"Gemini Memory Synthesis Error: {e}")
        return "I found a note, but I'm having trouble reading it right now."