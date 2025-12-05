import requests
import os
from dotenv import load_dotenv

load_dotenv()

MURF_API_KEY = os.getenv('MURF_API_KEY')

def generate_speech(text):
    url = "https://api.murf.ai/v1/speech/generate-with-key"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": MURF_API_KEY
    }
    
    payload = {
        "text": text,
        "voiceId": "en-US-Alicia",
        "style": "Conversational",
        "rate": 0,
        "pitch": 0,
        "sampleRate": 48000,
        "format": "MP3",
        "channelType": "STEREO",
        "pronunciationDictionary": {},
        "encodeAsBase64": True,
        "variation": 1,
        "audioDuration": 0,
        "modelVersion": "gen2"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if 'encodedAudio' in result and result['encodedAudio']:
            return result['encodedAudio']
        
        raise Exception("No audio data in Murf response")
    
    except Exception as e:
        print(f"Murf API error: {str(e)}")
        # Return empty string or handle gracefully in frontend
        raise Exception(f"Text-to-speech generation failed: {str(e)}")  
