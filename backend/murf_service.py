import requests
import os
<<<<<<< HEAD
=======
import base64
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
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
<<<<<<< HEAD
        "voiceId": "en-US-Alicia",
=======
        "voiceId": "en-US-ken",
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
        "style": "Conversational",
        "rate": 0,
        "pitch": 0,
        "sampleRate": 48000,
        "format": "MP3",
        "channelType": "STEREO",
        "pronunciationDictionary": {},
<<<<<<< HEAD
        "encodeAsBase64": True,
=======
        "encodeAsBase64": False,
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
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
        
<<<<<<< HEAD
=======
        if 'audioFile' in result and result['audioFile']:
            audio_url = result['audioFile']
            audio_response = requests.get(audio_url)
            audio_bytes = audio_response.content
            return base64.b64encode(audio_bytes).decode('utf-8')
        
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
        raise Exception("No audio data in Murf response")
    
    except Exception as e:
        print(f"Murf API error: {str(e)}")
<<<<<<< HEAD
        # Return empty string or handle gracefully in frontend
        raise Exception(f"Text-to-speech generation failed: {str(e)}")  
=======
        raise Exception(f"Text-to-speech generation failed: {str(e)}")
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
