import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: Gemini API key not found.")
    raise SystemExit(1)

client = genai.Client(api_key=api_key)

print("Testing Gemini 3.8 Flash...")

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Reply with exactly: Gemini API working"
    )

    print("\nSUCCESS!")
    print("Gemini response:", response.text)

except Exception as error:
    print("\nAPI TEST FAILED")
    print("Error:", error)