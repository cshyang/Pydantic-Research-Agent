"""Configuration management for the research agent."""
from pathlib import Path
from dotenv import load_dotenv
import os

# Get the project root directory
ROOT_DIR = Path(__file__).parent

# Load environment variables at module import time
load_dotenv(ROOT_DIR / ".env")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model Configuration
DEFAULT_MODEL = "openai:gpt-4o"
FAST_MODEL = "openai:gpt-4o-mini"

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable is not set")
