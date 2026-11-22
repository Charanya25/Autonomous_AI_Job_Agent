
import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: Gemini API key not found in .env")
else:
    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Explain artificial intelligence in 2 simple sentences."
        )

        print("\nGEMINI CONNECTION SUCCESSFUL!")
        print("\nGemini response:")
        print(response.text)

    except Exception as error:
        print("\nGEMINI CONNECTION FAILED!")
        print("Error:", error)
