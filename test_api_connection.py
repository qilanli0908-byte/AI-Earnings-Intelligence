
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

assert api_key and api_key != "your_api_key_here", (
    "Please configure a real API key in .env"
)

client = OpenAI(api_key=api_key, timeout=15.0)

try:
    client.models.list()
    print("PASS: OpenAI API connection successful.")

except Exception as error:
    print(f"Connection failed: {type(error).__name__}")
    print("Check your API key, network connection, and API project settings.")
