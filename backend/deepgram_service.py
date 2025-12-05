import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

def transcribe_audio(audio_data):
    try:
        url = "https://api.deepgram.com/v1/listen?model=nova-2&punctuate=true&language=en"
        
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/webm"
        }
        
        # Switched to synchronous requests
        response = requests.post(url, headers=headers, data=audio_data, timeout=30)
        
        if response.status_code != 200:
            print(f"Deepgram Error Details: {response.text}")
            return None
        
        result = response.json()
        
        # Safety check for nested keys
        if 'results' in result and 'channels' in result['results']:
            transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
            
            if not transcript or transcript.strip() == "":
                return None
            return transcript  
        return None
    
    except Exception as e:
        print(f"Deepgram error: {str(e)}")
        return None