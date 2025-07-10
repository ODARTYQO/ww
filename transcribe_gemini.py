import sys
import os
import google.generativeai as genai

if len(sys.argv) < 2:
    print("Usage: python transcribe_gemini.py <audio_file>")
    sys.exit(1)

audio_file = sys.argv[1]
api_key = os.environ.get("AIzaSyA94q9D4tADiLX0Ds557HxhG")

if not api_key:
    print("GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

with open(audio_file, "rb") as f:
    audio_data = f.read()

response = model.generate_content(
    [audio_data],
    generation_config={"language": "he"},
    request_options={"timeout": 600}
)

with open("transcript.txt", "w", encoding="utf-8") as out:
    out.write(response.text)

print("Transcription complete. Output saved to transcript.txt")
