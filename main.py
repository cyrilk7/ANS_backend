# Load environment variables from .env file
import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv('USER'))