import logging
from datetime import datetime, timedelta
import database as db
import llm_service
import memory_vector_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        try:
            # 1. Gather Real-time Context
            pending_tasks = [t for t in db.get_all_tasks(self.patient_id) if not t['completed']]
            
            # We get the last 3 turns for context
            recent_history = db.get_recent_conversations(self.patient_id, limit=3)
            
            # 2. Router: Ask LLM what the user wants
            # We now pass 'recent_history' to the function
            ai_decision = llm_service.get_ai_response(user_speech, pending_tasks, recent_history)
            
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
                return "I understand you are upset. I am going to contact your caregiver to help you right now."

            return initial_response

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return "I'm sorry, I'm having a little trouble thinking right now. Let's try again in a moment."

    # ------------------------------------------------------------------
    # ACTION HANDLERS
    # ------------------------------------------------------------------

    def _handle_task_logic(self, params, response_text, pending_tasks):
        action = params.get("action") 
        target_task = params.get("task_name")
        time_param = params.get("time")

        # 1. COMPLETION LOGIC
        if action == "complete" and target_task:
            # Case-insensitive check
            task_exists = any(t['task_name'].lower() == target_task.lower() for t in pending_tasks)
            
            if task_exists:
                db_task_name = next((t['task_name'] for t in pending_tasks if t['task_name'].lower() == target_task.lower()), target_task)
                db.mark_task_completed(self.patient_id, db_task_name)
                return response_text
            else:
                return "You've already finished that task today!"

        # 2. CREATION LOGIC
        elif action == "create":
            # If we have a task name but NO time, ask for it
            if target_task and not time_param:
                return f"At what time would you like to schedule {target_task.replace('_', ' ')}?"
            
            # If we have BOTH (because the LLM found the name in history), save it.
            if target_task and time_param:
                try:
                    # Clean time string
                    clean_time = time_param.lower().replace("pm","").replace("am","").strip()
                    if ":" not in clean_time:
                        hour = int(clean_time)
                        
                        if "pm" in str(params.get("raw_time", "")).lower() and hour < 12:
                             hour += 12
                        time_param = f"{hour:02d}:00"
                except:
                    time_param = "12:00" 

                # SAVE TO DB
                success = db.create_task(self.patient_id, target_task, time_param)
                
                if success:
                    return f"Okay, I've added {target_task.replace('_', ' ')} for {time_param}."
                else:
                    return f"You already have {target_task} on your list."

        return response_text

    def _handle_memory_save(self, user_speech, response_text, params):
        """
        Saves memory to BOTH SQL (for logs) and Vector DB (for search).
        """
        # 1. Save to SQLite (Structured Log)
        reminder_time = params.get("due_datetime")
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
        tasks = db.get_all_tasks(self.patient_id)
        current_time = datetime.now()
        missed = []
        
        for task in tasks:
            if not task['completed']:
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
