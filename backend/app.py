from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

import database as db
from conversation_engine import DementiaCompanion
from murf_service import generate_speech
from deepgram_service import transcribe_audio

load_dotenv()
required_keys = ['FLASK_SECRET_KEY', 'DEEPGRAM_API_KEY', 'MURF_API_KEY', 'GOOGLE_API_KEY']
missing = [k for k in required_keys if not os.getenv(k)]
if missing:
    raise EnvironmentError(f"Missing API keys: {missing}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
CORS(app)

db.init_database()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_text = None
        
        # 1. Check for Text Input (JSON)
        if request.is_json:
            data = request.get_json()
            user_text = data.get('message')
            if not user_text:
                return jsonify({'error': 'No message provided'}), 400

        # 2. Check for Audio Input ]
        elif 'audio' in request.files:
            audio_file = request.files['audio']
            audio_data = audio_file.read()
            # Transcribe
            user_text = transcribe_audio(audio_data) # 
            
            if user_text is None:
                # Handle transcription failure
                response_text = "I didn't catch that clearly. Could you say it again?"
                audio_base64 = generate_speech(response_text)
                return jsonify({
                    'transcript': "",
                    'response': response_text,
                    'audio': audio_base64
                })
        
        else:
            return jsonify({'error': 'Invalid content type. Send JSON or Audio file.'}), 400

        # 3. Process the Input 
        patient_id = db.get_patient_id()
        if not patient_id:
            return jsonify({'error': 'Patient not found'}), 404

        companion = DementiaCompanion(patient_id)
        
        # Pass the text to the engine 
        response_text = companion.process_input(user_text)
        
        # Save to DB 
        db.save_conversation(patient_id, user_text, response_text)
        
        # Generate Audio response 
        audio_base64 = generate_speech(response_text)
        
        return jsonify({
            'transcript': user_text,
            'response': response_text, 
            'audio': audio_base64      
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        patient_id = db.get_patient_id()
        tasks = db.get_all_tasks(patient_id)
        return jsonify(tasks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    try:
        patient_id = db.get_patient_id()
        notes = db.get_memory_notes(patient_id)
        return jsonify(notes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/caregiver-alert', methods=['GET'])
def caregiver_alert():
    try:
        patient_id = db.get_patient_id()
        companion = DementiaCompanion(patient_id)
        missed_tasks = companion.check_missed_tasks()
        
        if missed_tasks:
            alert_message = f"Patient missed: {', '.join(missed_tasks)}"
            return jsonify({'alert': alert_message, 'tasks': missed_tasks})
        
        return jsonify({'alert': None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        patient_id = db.get_patient_id()
        history = db.get_recent_conversations(patient_id, limit=10) 
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/record-call', methods=['POST'])
def record_call():
    try:
        data = request.json
        caller_name = data.get('caller_name')
        
        if not caller_name:
            return jsonify({'error': 'Caller name required'}), 400
        
        patient_id = db.get_patient_id()
        db.record_contact_call(patient_id, caller_name)
        
        return jsonify({'message': 'Call recorded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        data = request.json
        # Check if 'completed' is provided in the JSON body
        if 'completed' not in data:
            return jsonify({'error': 'Missing completed status'}), 400

        # Call the new database function
        db.update_task_status(task_id, data['completed'])
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
