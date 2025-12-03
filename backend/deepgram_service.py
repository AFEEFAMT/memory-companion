import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

async def transcribe_audio(audio_data):
    try:
        url = "https://api.deepgram.com/v1/listen?model=nova-2&punctuate=true&language=en"
        
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/wav"
        }
        
        response = requests.post(url, headers=headers, data=audio_data, timeout=30)
        
        if response.status_code != 200:
            print(f"Deepgram Error Details: {response.text}")
            return "I didn't catch that clearly"
        
        result = response.json()
        transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
        
        if not transcript or transcript.strip() == "":
            return "I didn't hear anything"
        
        return transcript
    
    except Exception as e:
        print(f"Deepgram error: {str(e)}")
        return "I had trouble understanding that"
