# KAYA - AI-Powered Memory Companion for Dementia Care

**Techfest IIT Bombay x Murf Voice Agent Hackathon 2025-26**  
**Team:** AFEEFA M T & AZIL SYED E K  

![App Screenshot](application_interface.png)  

## Overview

KAYA is a voice-activated memory assistant designed for patients with early-stage dementia. It maintains long-term contextual memory to recall personal details, manage medication schedules, and provide caregiver safety alerts through an empathetic conversational interface.

## Tech Stack

- **Voice Generation:** Murf.ai Falcon/Gen2 (Voice: Alicia)
- **Speech-to-Text:** Deepgram Nova-2
- **AI Engine:** Google Gemini 2.0 Flash
- **Vector Memory:** ChromaDB (semantic storage)
- **Database:** SQLite (structured task data)
- **Backend:** Python 3.10 / Flask
- **Frontend:** Vanilla JavaScript / HTML5

## Features

- **Conversational Memory:** RAG-powered recall of past conversations
- **Smart Scheduling:** Natural language task parsing ("Remind me to take medicine at 9 AM")
- **Caregiver Alerts:** Automatic notifications for missed tasks
- **Low Latency:** Optimized Murf Falcon integration for natural conversation flow

## Setup

### Prerequisites
Python 3.10+, API keys for Murf.ai, Deepgram, and Google Gemini

### Installation

```

git clone https://github.com/AFEEFAMT/memory-companion.git
cd memory-companion
cd backend
pip install -r requirements.txt

```

Create `.env` file in `backend/` directory:

```

FLASK_SECRET_KEY=your_random_secret_string
DEEPGRAM_API_KEY=your_deepgram_key
MURF_API_KEY=your_murf_key
GOOGLE_API_KEY=your_google_gemini_key

```

### Run

Open two terminals:

**Terminal 1 (Backend):**
```

cd backend
python app.py

```

**Terminal 2 (Frontend):**
```

cd frontend
python -m http.server 8000

```

Access at: `http://localhost:8000`

## Usage

- **Voice Input:** Hold microphone button, speak, release to send
- **Schedule Task:** Say "Remind me to take blood pressure medicine at 8 PM"
- **Recall Memory:** Ask "What did I say about my doctor?"
- **Caregiver Alert:** Red banner appears if task overdue by 1+ hour

## API Endpoints

**POST** `/api/chat` - Main interaction endpoint. Accepts text (JSON) or audio (FormData), returns text and base64 audio.  
**GET** `/api/history` - Fetches the recent conversation history for the UI.   
**GET** `/api/tasks` - Retrieves the list of scheduled tasks for the sidebar.   
**PUT** `/api/tasks/<task_id>` - Updates a task's status (e.g., marks it as completed).  
**GET** `/api/notes` - Retrieves stored memory notes for the sidebar.   
**GET** `/api/caregiver-alert` - Polled every 60s. Returns `true` if tasks are overdue by 1+ hour.   
**POST** `/api/record-call` - Logs external calls from family members into the database.   
## Demo Scenarios

**Memory Storage:**
> "My grandson's name is Rahul" → Stored in vector memory

**Task Creation:**
> "Remind me to call Dr. Sharma at 3 PM tomorrow" → Task scheduled

**Memory Retrieval:**
> "What's my grandson's name?" → "Your grandson's name is Rahul"

**Alert System:**
> 9 AM medicine reminder missed → Caregiver alert at 10 AM

## Architecture

1. User speaks → Deepgram transcribes
2. Gemini 2.0 processes intent + retrieves context from ChromaDB
3. Response generated + stored in SQLite/ChromaDB
4. Murf Falcon converts text to natural speech
5. Audio streamed back to user


## Contact

**GitHub:** [AFEEFA M T](https://github.com/AFEEFAMT), [AZIL SYED E K](https://github.com/achill06)

---

*Built with care for dementia patients and caregivers*




