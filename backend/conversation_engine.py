<<<<<<< HEAD
import logging
from datetime import datetime, timedelta
import database as db
import llm_service
import memory_vector_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
=======
from datetime import datetime, timedelta
import re
import database as db
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea

class DementiaCompanion:
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.patient_name = self.get_patient_name()
        
    def get_patient_name(self):
        conn = db.get_db_connection()
        patient = conn.execute("SELECT name FROM patients WHERE id = ?", (self.patient_id,)).fetchone()
        conn.close()
        return patient['name'] if patient else "friend"
    
    def process_input(self, user_speech):
<<<<<<< HEAD
        try:
            # 1. Gather Real-time Context
            pending_tasks = [t for t in db.get_all_tasks(self.patient_id) if not t['completed']]
            
            # 2. Router: Ask LLM what the user wants
            # Returns a dict: {"intent": "...", "response_text": "...", "parameters": {...}}
            ai_decision = llm_service.get_ai_response(user_speech, pending_tasks)
            
            intent = ai_decision.get("intent")
            initial_response = ai_decision.get("response_text")
            params = ai_decision.get("parameters", {})
            
            logger.info(f"User: {user_speech} | Intent: {intent}")

            # 3. Execute Logic based on Intent
            if intent == "manage_task":
                return self._handle_task_logic(params, initial_response, pending_tasks)
            
            elif intent == "save_memory":
                return self._handle_memory_save(user_speech, initial_response, params)
                
            elif intent == "recall_memory":
                return self._handle_memory_recall(user_speech)
            
            elif intent == "danger":
                # Immediate safety protocol (could trigger SMS alerts here)
                return "I understand you are upset. I am going to contact your caregiver to help you right now."

            # Default/Chat intent: Return the LLM's conversational response
            return initial_response

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return "I'm sorry, I'm having a little trouble thinking right now. Let's try again in a moment."

    # ------------------------------------------------------------------
    # ACTION HANDLERS
    # ------------------------------------------------------------------

    def _handle_task_logic(self, params, response_text, pending_tasks):
        """
        Updates database if LLM detects a task completion.
        """
        action = params.get("action") 
        target_task = params.get("task_name")

        if action == "complete" and target_task:
            # Verify task is actually pending to avoid double-marking
            task_exists = any(t['task_name'] == target_task for t in pending_tasks)
            
            if task_exists:
                db.mark_task_completed(self.patient_id, target_task)
                # The LLM has already generated a "Good job!" response in 'response_text'
                return response_text
            else:
                return "You've already finished that task today! You are doing great."
        
        return response_text

    def _handle_memory_save(self, user_speech, response_text, params):
        """
        Saves memory to BOTH SQL (for logs) and Vector DB (for search).
        """
        # 1. Save to SQLite (Structured Log)
        reminder_time = params.get("due_datetime") # Extracted by LLM
        db.add_memory_note(self.patient_id, user_speech, reminder_time)
        
        # 2. Save to Vector Store (Semantic Search)
        metadata = {
            "patient_id": self.patient_id,
            "date": datetime.now().isoformat(),
            "type": "general_note"
        }
        memory_vector_service.save_vector_memory(user_speech, metadata)
        
        return response_text

    def _handle_memory_recall(self, user_query):
        # 1. Search Vector DB
        found_notes = memory_vector_service.search_similar_memories(user_query)
        
        if not found_notes:
            return "I don't have a note about that, but I can write it down if you tell me."

        # 2. Contextualize for LLM
        context_str = "\n".join([f"- {n['text']} (Date: {n['metadata']['date'][:10]})" for n in found_notes])
        
        # 3. Generate Answer
        final_answer = llm_service.synthesize_memory_answer(user_query, context_str)
        return final_answer

    # ------------------------------------------------------------------
    # UTILITIES
    # ------------------------------------------------------------------

    def check_missed_tasks(self):
        """
        Used by the caregiver-alert endpoint to check for overdue items.
        """
=======
        user_speech_lower = user_speech.lower()
        
        if self.is_greeting(user_speech_lower):
            return self.greeting_response()
        
        if self.is_task_completion(user_speech_lower):
            return self.handle_task_completion(user_speech_lower)
        
        if self.is_asking_tasks(user_speech_lower):
            return self.list_pending_tasks()
        
        if self.is_creating_note(user_speech_lower):
            return self.create_memory_note(user_speech)
        
        if self.is_asking_notes(user_speech_lower):
            return self.recall_memory_notes()
        
        if self.is_asking_recent_caller(user_speech_lower):
            return self.remind_recent_caller()
        
        if self.is_setting_reminder(user_speech_lower):
            return self.set_reminder(user_speech)
        
        return self.contextual_response(user_speech)
    
    def is_greeting(self, text):
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in text for greeting in greetings)
    
    def is_task_completion(self, text):
        completion_words = ['done', 'finished', 'took', 'ate', 'completed', 'had', 'did']
        return any(word in text for word in completion_words)
    
    def is_asking_tasks(self, text):
        task_queries = ['what', 'tasks', 'todo', 'do', 'schedule', 'need to do']
        return any(query in text for query in task_queries)
    
    def is_creating_note(self, text):
        note_words = ['remember', 'note', 'write down', 'dont forget', "don't forget"]
        return any(word in text for word in note_words)
    
    def is_asking_notes(self, text):
        recall_words = ['what did i', 'what was', 'notes', 'tell me', 'remind me what']
        return any(word in text for word in recall_words)
    
    def is_asking_recent_caller(self, text):
        caller_queries = ['who called', 'who phone', 'who rang', 'missed call']
        return any(query in text for query in caller_queries)
    
    def is_setting_reminder(self, text):
        return 'remind' in text and ('tomorrow' in text or 'later' in text or 'hour' in text or 'day' in text)
    
    def greeting_response(self):
        return f"Hello {self.patient_name}. How are you feeling today? Would you like to know about your tasks?"
    
    def handle_task_completion(self, text):
        task_mapping = {
            'medicine': 'morning_medicine',
            'tablet': 'morning_medicine',
            'pill': 'morning_medicine',
            'breakfast': 'breakfast',
            'lunch': 'lunch',
            'walk': 'evening_walk',
            'exercise': 'evening_walk',
            'dinner': 'dinner',
            'supper': 'dinner'
        }
        
        for keyword, task_name in task_mapping.items():
            if keyword in text:
                db.mark_task_completed(self.patient_id, task_name)
                return self.positive_reinforcement(task_name)
        
        return "That's wonderful. You're doing a great job today. What else have you done?"
    
    def positive_reinforcement(self, task_name):
        responses = {
            'morning_medicine': "Excellent work taking your medicine. That's very important for your health. Would you like to have your breakfast now?",
            'breakfast': "I'm glad you had your breakfast. Eating well gives you energy for the day. Remember to have your lunch later.",
            'lunch': "Good job having your lunch. You're staying on track today. How are you feeling?",
            'evening_walk': "Wonderful. Walking is great for you. I'm proud of you for staying active.",
            'dinner': "Well done having your dinner. You've had a good day today."
        }
        return responses.get(task_name, "That's great. You're doing wonderfully.")
    
    def list_pending_tasks(self):
        tasks = db.get_all_tasks(self.patient_id)
        pending = [t for t in tasks if not t['completed']]
        
        if not pending:
            return "You've done all your tasks for today. You should be very proud of yourself."
        
        task_descriptions = {
            'morning_medicine': 'take your morning medicine',
            'breakfast': 'have your breakfast',
            'lunch': 'have your lunch',
            'evening_walk': 'go for your evening walk',
            'dinner': 'have your dinner',
            'night_medicine': 'take your night medicine'
        }
        
        if len(pending) == 1:
            task_desc = task_descriptions.get(pending[0]['task_name'], pending[0]['task_name'])
            return f"You still need to {task_desc}. Shall we do that now?"
        
        task_list = [task_descriptions.get(t['task_name'], t['task_name']) for t in pending[:3]]
        return f"Let me help you. You still need to: {', '.join(task_list[:-1])}, and {task_list[-1]}. Let's start with the first one."
    
    def create_memory_note(self, text):
        note_text = text
        reminder_time = self.extract_reminder_time(text)
        
        db.add_memory_note(self.patient_id, note_text, reminder_time)
        
        if reminder_time:
            return f"I've made a note of that and I'll remind you at {reminder_time}. Don't worry, I'm here to help you remember."
        return "I've written that down for you. You can ask me about it anytime. I'm here to help."
    
    def recall_memory_notes(self):
        notes = db.get_memory_notes(self.patient_id)
        
        if not notes:
            return "You haven't asked me to remember anything yet. But I'm here whenever you need me."
        
        recent_note = notes[0]
        return f"You asked me to remember this: {recent_note['note_text']}. Would you like to hear more?"
    
    def remind_recent_caller(self):
        caller = db.get_recent_caller(self.patient_id)
        
        if not caller:
            return "I don't have a record of recent calls. But I'm here if you need anything."
        
        call_time = datetime.fromisoformat(caller['call_time'])
        time_ago = self.humanize_time_difference(datetime.now() - call_time)
        
        return f"{caller['caller_name']} called you {time_ago}. Would you like to call them back?"
    
    def set_reminder(self, text):
        reminder_time = self.extract_reminder_time(text)
        db.add_memory_note(self.patient_id, text, reminder_time)
        
        return f"I'll remind you about that. Don't worry, I won't forget."
    
    def contextual_response(self, text):
        recent_convs = db.get_recent_conversations(self.patient_id, limit=3)
        
        gentle_responses = [
            "I'm here to help you. Would you like to know about your tasks?",
            "Take your time. How can I help you today?",
            "I'm listening carefully. You can ask me about your tasks, or ask me to remember something.",
            "That's okay. Would you like me to remind you about your medicine or meals?"
        ]
        
        import random
        return random.choice(gentle_responses)
    
    def extract_reminder_time(self, text):
        if 'tomorrow' in text:
            match = re.search(r'(\d{1,2})\s*(am|pm|hour)', text.lower())
            if match:
                hour = match.group(1)
                period = match.group(2)
                tomorrow = datetime.now() + timedelta(days=1)
                return f"{tomorrow.strftime('%Y-%m-%d')} {hour}:00 {period}"
        
        if 'hour' in text:
            match = re.search(r'(\d+)\s*hour', text.lower())
            if match:
                hours = int(match.group(1))
                reminder_time = datetime.now() + timedelta(hours=hours)
                return reminder_time.strftime('%Y-%m-%d %H:%M')
        
        return None
    
    def humanize_time_difference(self, td):
        if td.days > 0:
            return f"{td.days} day{'s' if td.days > 1 else ''} ago"
        hours = td.seconds // 3600
        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        minutes = td.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    
    def check_missed_tasks(self):
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
        tasks = db.get_all_tasks(self.patient_id)
        current_time = datetime.now()
        missed = []
        
        for task in tasks:
            if not task['completed']:
<<<<<<< HEAD
                # Parse scheduled time
                try:
                    task_time = datetime.strptime(task['scheduled_time'], '%H:%M').time()
                    scheduled_datetime = datetime.combine(datetime.today(), task_time)
                    
                    # If 1 hour past schedule
                    if current_time > scheduled_datetime + timedelta(hours=1):
                        missed.append(task['task_name'].replace('_', ' '))
                except ValueError:
                    continue # Skip invalid time formats
        
        return missed
=======
                task_time = datetime.strptime(task['scheduled_time'], '%H:%M').time()
                scheduled_datetime = datetime.combine(datetime.today(), task_time)
                
                if current_time > scheduled_datetime + timedelta(hours=1):
                    missed.append(task['task_name'].replace('_', ' '))
        
        return missed
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
