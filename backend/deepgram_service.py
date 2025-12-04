import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

<<<<<<< HEAD
def transcribe_audio(audio_data):
=======
async def transcribe_audio(audio_data):
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
    try:
        url = "https://api.deepgram.com/v1/listen?model=nova-2&punctuate=true&language=en"
        
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
<<<<<<< HEAD
            "Content-Type": "audio/webm"
        }
        
        # Switched to synchronous requests
=======
            "Content-Type": "audio/wav"
        }
        
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
        response = requests.post(url, headers=headers, data=audio_data, timeout=30)
        
        if response.status_code != 200:
            print(f"Deepgram Error Details: {response.text}")
            return "I didn't catch that clearly"
        
        result = response.json()
<<<<<<< HEAD
        
        # Safety check for nested keys
        if 'results' in result and 'channels' in result['results']:
            transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
            
            if not transcript or transcript.strip() == "":
                return "I didn't hear anything"
            return transcript  
        return "I didn't hear anything"
    
    except Exception as e:
        print(f"Deepgram error: {str(e)}")
        return "I had trouble understanding that"
=======
        transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
        
        if not transcript or transcript.strip() == "":
            return "I didn't hear anything"
        
        return transcript
    
    except Exception as e:
        print(f"Deepgram error: {str(e)}")
        return "I had trouble understanding that"
>>>>>>> 5a8867ea84c8aeabb188a7f99107c15e21a432ea
