import sys
import os
from dotenv import load_dotenv

# Load API keys from .env file before anything else
load_dotenv()

from src.replicability_audit.cli import app

if __name__ == "__main__":
    app()
