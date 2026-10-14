
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

assert api_key is not None, (
    "OPENAI_API_KEY was not found in the .env file."
)

print("PASS: AI environment configuration loaded.")

if api_key == "your_api_key_here":
    print("API key is currently a placeholder.")
else:
    print("API key is configured.")

# Never print the actual API key.
