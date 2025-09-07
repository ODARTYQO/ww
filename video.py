import ssl
import urllib3

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
import time
import google.generativeai as genai

# הגדרת המפתח
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBNnR0YAg5Q6BTCc69lMkylugx3fduRE60")
genai.configure(api_key=GEMINI_API_KEY)

prompt = """A close up of two people staring at a cryptic drawing on a wall, torchlight flickering.

A man murmurs, 'This must be it. That's the secret code.' The woman looks at him and whispering excitedly, 'What did you find?'"""

# יצירת אובייקט מודל
model = genai.GenerativeModel("veo-3.0-generate-preview")

# התחלת יצירת הווידאו
operation = model.generate_video(prompt=prompt)

# המתנה לסיום
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = genai.get_operation(operation.name)

# הורדת הווידאו
video = operation.response.generated_videos[0]

with open("dialogue_example.mp4", "wb") as f:
    f.write(video.content)

print("Generated video saved to dialogue_example.mp4")
