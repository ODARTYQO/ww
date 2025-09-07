import ssl
import urllib3

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
import time
from google import genai

# ודא שהמפתח מוגדר בסביבה או השתמש בערך ברירת מחדל
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBNnR0YAg5Q6BTCc69lMkylugx3fduRE60")

# העבר את המפתח ללקוח (אם נדרש)
client = genai.Client(api_key=GEMINI_API_KEY)

prompt = """A close up of two people staring at a cryptic drawing on a wall, torchlight flickering.

A man murmurs, 'This must be it. That's the secret code.' The woman looks at him and whispering excitedly, 'What did you find?'"""

# Start the generation job
operation = client.models.generate_videos(
    model="veo-3.0-generate-preview",
    prompt=prompt,
)

# Poll for the result
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation.name)

# Download the final video
# ודא שמבנה התגובה נכון
video = operation.response.generated_videos[0]

# שמור את הווידאו (בהנחה שזה אובייקט עם שדה content)
with open("dialogue_example.mp4", "wb") as f:
    f.write(video.content)

print("Generated video saved to dialogue_example.mp4")
