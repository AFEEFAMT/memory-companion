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
3. "parameters": (Optional) Data needed for the intent.

RULES FOR TASKS & CONTEXT:
1. **NEW TASK**: If User says "Add [Task]", output intent="manage_task", action="create", and "task_name"="[Task]". If the time is not stated, leave "time" null.
2. **SLOT FILLING (CRITICAL)**: If the User replies with JUST a time (e.g., "11 pm", "at 9", "9:00"), you MUST check the "RECENT CONVERSATION HISTORY". 
   - Look at what the Agent (You) JUST asked. 
   - If you asked "At what time would you like to schedule [Task]?", you MUST use that [Task] name.
   - Output: intent="manage_task", action="create", task_name="[The Task from history]", time="[User's Time]".
3. **TIME FORMAT**: Convert all times to 24-hour HH:MM format (e.g., convert "5 pm" to "17:00", "9 am" to "09:00").

For "manage_task", always include "action": "complete" OR "create".
For "create", include "task_name" and "time" (HH:MM format).
"""

def get_ai_response(user_text, pending_tasks_list, recent_history):
    try:
        current_time = datetime.now().strftime("%A, %I:%M %p")
        tasks_str = ", ".join([t['task_name'] for t in pending_tasks_list]) or "None"
        
        history_str = ""
        if recent_history:
            # Reverse history so it flows chronologically (Oldest -> Newest)
            for turn in reversed(recent_history):
                history_str += f"User: {turn['user_message']}\nKaya: {turn['agent_response']}\n"
        
        # Inject history into the prompt
        formatted_system_prompt = SYSTEM_INSTRUCTION.format(
            current_time=current_time, 
            pending_tasks=tasks_str
        )
        
        # We append the history strictly to the context
        full_prompt = f"""
        {formatted_system_prompt}

        RECENT CONVERSATION HISTORY:
        {history_str}
        
        USER'S NEW INPUT:
        {user_text}
        """

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        response = model.generate_content(full_prompt)
        clean_text = re.sub(r"```(json)?", "", response.text, flags=re.IGNORECASE).strip()
        return json.loads(clean_text)

    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
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